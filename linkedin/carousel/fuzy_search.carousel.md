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

# Slide 3 — Levenshtein

## Title

### **Levenshtein Distance**

## Body

The classic algorithm behind most fuzzy search systems.

It counts how many edits turn one word into another:

* insertions
* deletions
* substitutions

Smaller distance = more similar words.

Example:
`apple` → `aple`
→ 1 deletion → distance of 1

Under the hood it’s solved with dynamic programming.

---

# Slide 4 — Damerau-Levenshtein

## Title

### **Damerau-Levenshtein**

## Body

A small twist on Levenshtein — but a meaningful one.

It adds a fourth allowed operation:

* transposing two adjacent letters

Example:
`form` → `from`

* Levenshtein → distance of 2
* Damerau-Levenshtein → distance of 1

This matters because humans swap letters all the time when typing fast.

---

# Slide 5 — N-Grams

## Title

### **N-Grams**

## Body

A completely different approach: split text into small chunks and compare overlap.

Example with bigrams (n=2):

* `helo` → [`he`, `el`, `lo`]
* `hello` → [`he`, `el`, `ll`, `lo`]

Lots of overlap = high similarity.

Great for:

* longer strings
* full-text search
* situations where edit distance gets expensive

---

# Slide 6 — Libraries

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

# Slide 7 — The Trade-offs

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

# Slide 8 — Scaling It Up

## Title

### **Making It Fast**

## Body

Fuzzy search can get expensive on large datasets.

A few ways to keep it snappy:

* pre-computation
  → store common search terms and their variants

* query optimization
  → limit returned items and cache frequent searches

* indexing strategies
  → trigram or inverted indexes speed up lookups dramatically

Start simple. Scale only when you actually need to.

---

# Slide 9 — Elasticsearch

## Title

### **When You Outgrow DIY**

## Body

Eventually, hand-rolled fuzzy search hits a wall.

That’s where Elasticsearch shines:

* fuzzy queries supported out of the box
* tunable edit distance per query
* built on top of Lucene → fast even on huge datasets
* combines fuzzy match with ranking, filters, and analyzers

The catch:

* heavier to integrate
* extra infrastructure to maintain

Best for big systems where search quality is a core feature.

---

# Slide 10 — My Use Case

## Title

### **How I’m Using It**

## Body

I’m adding fuzzy match to Fonli, my language learning app.

The goal:

* if the user types something close enough to the correct answer
* count it as a hit instead of forcing an exact match

A small change, but a big UX win.

Because in 2026, “no results” is the fastest way to lose a user.
