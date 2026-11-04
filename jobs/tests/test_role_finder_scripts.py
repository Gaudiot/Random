import copy
from datetime import date
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from select_companies import select_companies
from role_finder_common import MANUAL_REVIEW_ROLE, valid_url
from update_available_from import update_available_from


TODAY = date(2026, 11, 3)


def company(name="Example", **overrides):
    return {"name": name, "url": f"https://example.com/{name}", "type": "Company", "available_from": "2026-11-03", **overrides}


class ScriptTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source = self.root / "opportunities.json"
        self.selection = self.root / "selection.json"
        self.roles = self.root / "open_roles.json"

    def write_source(self, entries):
        self.source.write_text(json.dumps({"applied_qtt": 1, "last_updated": "old", "opportunities": entries}), encoding="utf-8")

    def select(self, **kwargs):
        manifest, diagnostics = select_companies(self.source, today=TODAY, **kwargs)
        self.selection.write_text(json.dumps(manifest), encoding="utf-8")
        return manifest, diagnostics

    def write_roles(self, *names):
        self.roles.write_text(json.dumps([{"company_name": name, "role": "Engineer", "url": f"https://example.com/apply/{name}"} for name in names]), encoding="utf-8")

    def update(self, **kwargs):
        return update_available_from(self.source, self.roles, self.selection, today=TODAY, **kwargs)

    def test_cutoff_type_dates_url_order_and_limit(self):
        self.write_source([
            company("past", available_from="2026-11-02", type=" company "),
            company("future", available_from="2026-11-04"),
            company("board", type="Job Board"),
            company("today"), company("bad", available_from="2026-2-03"),
            company("invalid", available_from="2026-02-30"),
            company("hostless", url="https:///jobs"), company("ftp", url="ftp://example.com/jobs"),
            company("past", available_from="2026-11-02", type=" company "),
            company("last"), {}, None,
        ])
        manifest, diagnostics = self.select(limit=2)
        self.assertEqual([x["name"] for x in manifest["companies"]], ["past", "today"])
        self.assertEqual([x["source_index"] for x in manifest["companies"]], [0, 3])
        self.assertEqual(len(diagnostics), 9)
        self.assertEqual(self.select(limit=0)[0]["companies"], [])
        with self.assertRaises(ValueError): self.select(limit=-1)

    def test_url_host_and_port_validation(self):
        for url in ["https://example.com/jobs", "http://localhost/jobs", "https://[::1]/jobs", "https://exemplo.com.br"]:
            with self.subTest(url=url): self.assertTrue(valid_url(url))
        for url in ["https://example.com:invalid", "https://example.com:70000", "https://example.com:0", "https://-bad.com", "https://exa\\mple.com", "https:///jobs", "https://exa mple.com"]:
            with self.subTest(url=url): self.assertFalse(valid_url(url))

    def test_update_only_selected_companies_with_roles_and_preserve_other_data(self):
        entries = [company("one"), company("two"), company("three"), company("board", type="Job Board")]
        self.write_source(entries)
        original = json.loads(self.source.read_text())
        self.select(limit=2)
        self.write_roles("one", "one")
        result = self.update()
        expected = copy.deepcopy(original)
        expected["opportunities"][0]["available_from"] = "2026-11-17"
        self.assertEqual(json.loads(self.source.read_text()), expected)
        self.assertEqual(result["companies"], ["one"])

    def test_saved_roles_and_blocked_companies_share_cooldown_without_updating_no_matches(self):
        entries = [company("matched"), company("blocked"), company("no_matches"), company("unselected")]
        self.write_source(entries)
        original = self.source.read_bytes()
        expected = json.loads(original)
        self.select(limit=3)
        real_role = {"company_name": "matched", "role": "Engineer", "url": "https://example.com/apply/matched"}
        manual_review = {"company_name": "blocked", "role": MANUAL_REVIEW_ROLE, "url": entries[1]["url"]}
        self.roles.write_text(json.dumps([real_role, manual_review, manual_review]), encoding="utf-8")

        planned = self.update(dry_run=True)
        self.assertEqual(planned["companies"], ["matched", "blocked"])
        self.assertEqual(planned["available_from"], "2026-11-17")
        self.assertEqual(self.source.read_bytes(), original)

        result = self.update()
        expected["opportunities"][0]["available_from"] = "2026-11-17"
        expected["opportunities"][1]["available_from"] = "2026-11-17"
        self.assertEqual(json.loads(self.source.read_bytes()), expected)
        self.assertEqual(result["companies"], ["matched", "blocked"])

    def test_nonselected_manual_review_company_prevents_all_updates(self):
        entries = [company("matched"), company("not_selected")]
        self.write_source(entries)
        original = self.source.read_bytes()
        self.select(limit=1)
        results = [
            {"company_name": "matched", "role": "Engineer", "url": "https://example.com/apply/matched"},
            {"company_name": "not_selected", "role": MANUAL_REVIEW_ROLE, "url": entries[1]["url"]},
        ]
        self.roles.write_text(json.dumps(results), encoding="utf-8")
        for dry_run in (True, False):
            with self.subTest(dry_run=dry_run):
                with self.assertRaisesRegex(ValueError, "not selected"):
                    self.update(dry_run=dry_run)
                self.assertEqual(self.source.read_bytes(), original)

    def test_wrong_manual_review_url_prevents_all_updates(self):
        self.write_source([company("matched"), company("blocked")])
        original = self.source.read_bytes()
        self.select()
        results = [
            {"company_name": "matched", "role": "Engineer", "url": "https://example.com/apply/matched"},
            {"company_name": "blocked", "role": MANUAL_REVIEW_ROLE, "url": "https://example.com/fictional-application"},
        ]
        self.roles.write_text(json.dumps(results), encoding="utf-8")
        for dry_run in (True, False):
            with self.subTest(dry_run=dry_run):
                with self.assertRaisesRegex(ValueError, "manual-review URL must exactly match"):
                    self.update(dry_run=dry_run)
                self.assertEqual(self.source.read_bytes(), original)

    def test_execution_date_not_previous_date_or_selection_date(self):
        self.write_source([company("one", available_from="1999-01-13")])
        manifest, _ = select_companies(self.source, today=date(2026, 12, 30))
        self.selection.write_text(json.dumps(manifest))
        self.write_roles("one")
        result = update_available_from(self.source, self.roles, self.selection, today=date(2026, 12, 30))
        self.assertEqual(result["available_from"], "2027-01-13")

    def test_different_selection_day_is_rejected(self):
        self.write_source([company("one")])
        self.select()
        self.write_roles("one")
        original = self.source.read_bytes()
        with self.assertRaisesRegex(ValueError, "execution date"):
            update_available_from(self.source, self.roles, self.selection, today=date(2026, 11, 4))
        self.assertEqual(self.source.read_bytes(), original)

    def test_empty_roles_and_dry_run_preserve_exact_bytes(self):
        self.write_source([company("one")])
        self.select()
        original = self.source.read_bytes()
        self.write_roles()
        self.assertEqual(self.update()["companies"], [])
        self.assertEqual(self.source.read_bytes(), original)
        self.write_roles("one")
        self.assertEqual(self.update(dry_run=True)["companies"], ["one"])
        self.assertEqual(self.source.read_bytes(), original)

    def test_unknown_role_company_does_not_write(self):
        self.write_source([company("one"), company("two")])
        self.select(limit=1)
        self.write_roles("one", "two")
        original = self.source.read_bytes()
        with self.assertRaisesRegex(ValueError, "not selected"): self.update()
        self.assertEqual(self.source.read_bytes(), original)

    def test_changed_source_and_stale_manifest_are_rejected(self):
        self.write_source([company("one")])
        self.select()
        self.write_roles("one")
        self.update()
        original = self.source.read_bytes()
        with self.assertRaisesRegex(ValueError, "source changed"): self.update()
        self.assertEqual(self.source.read_bytes(), original)

    def test_ambiguous_company_names_are_rejected(self):
        self.write_source([company("same"), company("same", url="https://different.com")])
        self.select()
        self.write_roles("same")
        original = self.source.read_bytes()
        with self.assertRaisesRegex(ValueError, "ambiguous"): self.update()
        self.assertEqual(self.source.read_bytes(), original)

    def test_unmatched_ambiguous_names_do_not_block_other_updates(self):
        self.write_source([company("same"), company("same", url="https://different.com"), company("other")])
        self.select()
        self.write_roles("other")
        self.assertEqual(self.update()["companies"], ["other"])

    def test_identical_source_duplicates_refuse_update_even_beyond_limit(self):
        self.write_source([company("same"), company("other"), company("same")])
        self.write_roles("same")
        original = self.source.read_bytes()
        for limit in (None, 1):
            with self.subTest(limit=limit):
                manifest, _ = self.select(limit=limit)
                self.assertEqual(sum(x["name"] == "same" for x in manifest["companies"]), 1)
                with self.assertRaisesRegex(ValueError, "duplicate company/URL source entries"):
                    self.update()
                self.assertEqual(self.source.read_bytes(), original)

    def test_conflicting_duplicate_dates_skip_group_in_either_order(self):
        past = company("same", available_from="2026-11-02")
        future = company("same", available_from="2026-11-04")
        for entries in ([past, future], [future, past]):
            with self.subTest(entries=entries):
                self.write_source([*entries, company("other")])
                manifest, diagnostics = self.select(limit=1)
                self.assertEqual([x["name"] for x in manifest["companies"]], ["other"])
                self.assertEqual(len(diagnostics), 2)
                self.assertTrue(all("conflicting available_from" in message for message in diagnostics))

    def test_tampered_manifest_and_invalid_roles_do_not_write(self):
        self.write_source([company("one")])
        manifest, _ = self.select()
        self.write_roles("one")
        original = self.source.read_bytes()
        manifest["companies"][0]["name"] = "tampered"
        self.selection.write_text(json.dumps(manifest))
        with self.assertRaises(ValueError): self.update()
        self.assertEqual(self.source.read_bytes(), original)
        self.select()
        self.roles.write_text('[{"company_name":"one","role":"Engineer","url":"https://example.com","extra":1}]')
        with self.assertRaises(ValueError): self.update()
        self.assertEqual(self.source.read_bytes(), original)

    def test_atomic_replace_failure_preserves_source_and_removes_temporary(self):
        self.write_source([company("one")])
        self.select()
        self.write_roles("one")
        original = self.source.read_bytes()
        with patch("role_finder_common.os.replace", side_effect=OSError("cannot replace")):
            with self.assertRaises(OSError): self.update()
        self.assertEqual(self.source.read_bytes(), original)
        self.assertEqual(list(self.root.glob("*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
