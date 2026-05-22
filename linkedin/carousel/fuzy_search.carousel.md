---

# 🎠 Carrossel — Fuzzy Search

---

# Slide 1 — What is it?

## Title

### **What Is Fuzzy Search?**

## Body

Fuzzy search finds words that are close enough to a keyword — not just exact matches.

Searching for `victor` can match:

* victor
* vitor
* viktor
* victoria
* vitorr

It also ignores case, so `victor` and `VICTOR` are treated the same.

It’s how search forgives typos, misspellings, and OCR mistakes.

---

# Slide 2 — Where you’ve seen it

## Title

### **You’ve Seen It Everywhere**

## Body

Even if you didn’t know the name, you’ve been using it for years.

Common examples:

* finding a friend on Instagram
* searching cities on Google Maps
* looking up products on Amazon
* SQL lookups when you’re unsure of the spelling
* deduplicating records that don’t share a unique key

It works so well that users now expect it in every app.

---

# Slide 3 — The Algorithms

## Title

### **The Algorithms Behind It**

## Body

A few classic approaches power most fuzzy search systems.

* Levenshtein Distance
  → counts how many insertions, deletions, or substitutions turn one word into another
  → smaller distance = more similar
  → solved with dynamic programming under the hood

* Damerau-Levenshtein
  → same idea, but also allows swapping adjacent letters

* N-Grams
  → splits text into small chunks and compares overlap
  → bigrams of `Helo` → [`he`, `el`, `lo`]
  → bigrams of `Hello` → [`he`, `el`, `ll`, `lo`]
  → lots of overlap = high similarity

---

# Slide 4 — Libraries

## Title

### **Skip The Math**

## Body

You don’t need to implement any of this from scratch.

There are solid libraries that return a similarity score out of the box:

* Python → fuzzywuzzy
  → compares two strings and returns a 0–100 similarity score

* JavaScript → Fuse.js
  → lightweight fuzzy search across lists and objects

For most projects, picking a library is the right call.

---

# Slide 5 — The Trade-offs

## Title

### **The Trade-offs**

## Body

Fuzzy search is powerful, but it’s not magic.

Some things to keep in mind:

* it can return too many results
  → users may need to scan the whole list

* it only handles typos and misspellings
  → no synonyms, no semantic understanding

* similarity isn’t always relevance
  → searching for `car` might surface `air`, `card`, `can`

Tuning thresholds and ranking matters a lot.

---

# Slide 6 — Scaling It Up

## Title

### **Making It Fast**

## Body

Fuzzy search can get expensive on large datasets.

A few ways to keep it snappy:

* pre-computation
  → store common search terms and their variants

* query optimization
  → limit returned items and cache frequent searches

* dedicated search engines
  → ElasticSearch supports fuzzy search out of the box
  → great for big systems, but heavy to integrate

Start simple. Scale only when you need to.

---

# Slide 7 — My Use Case

## Title

### **How I’m Using It**

## Body

I’m adding fuzzy match to Fonli, my language learning app.

The goal:

* if the user types something close enough to the correct answer
* count it as a hit instead of forcing an exact match

A small change, but a big UX win.

Because in 2026, “no results” is the fastest way to lose a user.
