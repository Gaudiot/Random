# Job search and CV builder

This folder helps you find jobs and prepare a CV for a specific role. It uses two agents: `role-finder` and `resume-builder`.

## Set up

You need an assistant that can use the agent files, read and write local files, and browse company career pages. The helper scripts need Python 3.10 or later. They use only the Python standard library.

Keep the `jobs` folder at the root of your repository. Run the commands below from that root.

### 1. Add your profile

Edit `jobs/json-resume.json` with your own information: contact details, location, work history, achievements, education, skills, proficiency levels, and languages. Consult [jsonresume](https://jsonresume.org/schema) to see extra fields that can be added.

This file is the source of facts for both agents. Keep it accurate and up to date. The agents must not invent experience or skills.

### 2. Add a Word template

Place a `.docx` CV template inside `jobs`. You must provide this file yourself.

The current `resume-builder` instructions expect this exact path:

```text
jobs/CV_VictorGaudiot_Dev.docx
```

You can use that filename or choose your own, such as `jobs/CV_Template.docx`. If you rename it, update the template path in the `resume-builder` agent files you use:

- `.codex/agents/resume-builder.toml`
- `.claude/agents/resume-builder.md`

Also replace the personal output filename pattern in those files. It currently generates `jobs/[company_name]CV_VictorGaudiot_Dev.docx`.

Use a simple template with one column and clear sections such as Summary, Experience, Skills, and Education. The agent edits a copy and keeps the original template unchanged. It applies its formatting rules, including Arial text.

### 3. Add companies

Edit `jobs/opportunities.json`. A minimal example is:

```json
{
  "opportunities": [
    {
      "name": "Example Company",
      "url": "https://example.com/careers",
      "available_from": "2026-01-01",
      "type": "Company"
    }
  ]
}
```

Use the company's real career page or its recruiting page. `available_from` is the first date on which the company can be searched again. Use `YYYY-MM-DD`; today and past dates are eligible, future dates are skipped. Dates use the computer's local date.

`role-finder` searches only entries with type `Company`, ignoring case and surrounding spaces. It skips job boards. The existing `applied_qtt` and `last_updated` fields are optional metadata for this workflow.

## Find jobs with role-finder

Ask your assistant:

> Use role-finder to search the first 20 eligible companies. Only consider fully remote software engineering jobs that let me live in Brazil. CLT and contractor/PJ work are both acceptable.

State your own preferences in the request. Fully remote work is not a fixed default: the agent also considers compatible onsite or hybrid roles unless you restrict the search.

The agent selects eligible companies in file order, reads their job listings, and compares relevant roles with your profile. It checks location restrictions, job requirements, and application links. It uses public recruiting APIs when available and limits recovery attempts when a site fails.

It writes `jobs/open_roles.json`. Every entry has exactly three fields:

```json
[
  {
    "company_name": "Example Company",
    "role": "Software Engineer",
    "url": "https://example.com/careers/software-engineer/apply"
  }
]
```

If access remains blocked or unavailable, including a persistent 404, the agent adds the company for manual review. Its `role` is `Revisão manual — acesso bloqueado ou indisponível`, and its `url` is the company's starting career URL. This is not a confirmed vacancy. A working alternative source avoids this marker; missing information or lack of time alone does not create it.

After saving valid results, the agent sets `available_from` to the execution date plus **14 days** for companies included in the output. This includes manual-review entries. Companies only visited, or checked without a matching role, keep their dates. A new search replaces the previous results instead of keeping old vacancies.

The agent may create `selected_companies.json`, `role_finder_report.md`, and `role_finder_checkpoint.json` while working. It deletes them at the end, after updating and checking the dates. Important limitations are summarized in its final response.

## Build a CV with resume-builder

Give the agent a job URL or paste the full job description:

> Use resume-builder to prepare my CV for this role: [job URL or full description].

The agent reads the job description, your profile, and the Word template. It creates an English DOCX tailored to that role. It adapts the headline, supported work titles, summary, and achievement bullets. It removes unrelated skills and puts the most relevant ones first within their original proficiency levels.

Related experience can remain when useful. For example, Flutter can support a mobile application that asks for React Native, but the CV must still say Flutter. The agent must not claim you know a requested technology that is missing from your profile.

The original profile and template stay unchanged. The generated CV is saved in `jobs`, using the output name configured in the agent. Existing CVs are preserved with a numbered filename when needed. The agent reports skill gaps and validation results; any coverage estimate is not a guaranteed employer ATS score.

Neither agent submits applications for you. Finding jobs and building a CV are separate requests.

## Helper scripts

| File | Purpose |
| --- | --- |
| `scripts/select_companies.py` | Select eligible companies by type, date, name, URL, and optional limit. It does not browse websites. |
| `scripts/update_available_from.py` | Update dates only for selected companies included in the saved results. It checks the selection before writing. |
| `scripts/role_finder_common.py` | Shared functions for JSON files, dates, URLs, and safe saving. Do not run it directly. |
| `tests/test_role_finder_scripts.py` | Test the selection and date-update rules using temporary data. |

The agent normally runs the scripts for you. To run them yourself:

```sh
python jobs/scripts/select_companies.py --limit 20 --output jobs/selected_companies.json
```

Next, complete the job search for that selection and save its results in `jobs/open_roles.json`. Only then preview and apply the date changes:

```sh
python jobs/scripts/update_available_from.py --selection jobs/selected_companies.json --dry-run
python jobs/scripts/update_available_from.py --selection jobs/selected_companies.json
```

Use the selection on the same day it was created. Do not edit `opportunities.json` between selection and updating. After updating, the old selection is no longer valid. Do not create a new selection just to apply old results again.

When running this manually, remove the selection and any temporary report or checkpoint after all checks are finished. The scripts do not remove those files themselves. See [the script guide](scripts/README.md) for details.

To run the tests:

```sh
python -m unittest discover -s jobs/tests -p "test_*.py" -v
```

`jobs.py` is an older, optional browser helper. It opens eligible pages in batches and offers a separate three-week date update. It is not part of the agent workflow and is not needed for a clean setup.

## Start a clean repository

Copy only the files below, keeping the same folder structure. Choose the agent folder for your assistant, or keep both if you use both.

```text
.codex/agents/
  resume-builder.toml
  role-finder.toml
.claude/agents/
  resume-builder.md
  role-finder.md
jobs/
  README.md
  json-resume.json
  opportunities.json
  CV_Template.docx                 # supply your own; update the agent path
  scripts/
    README.md
    select_companies.py
    update_available_from.py
    role_finder_common.py
  tests/                          # optional, recommended
    test_role_finder_scripts.py
```

Replace the profile with your own data, add your Word template, choose your companies, and update the template and output names in the resume agent. You do not need the rest of this repository or its unrelated agents and skills.

Do not copy old `open_roles.json` results, generated company CVs, temporary support files, `__pycache__` folders, or one-off audit outputs. They are not setup files. The existing cover letter, job-description notes, and `jobs.py` are also optional. `open_roles.json` will be created by your first completed search.
