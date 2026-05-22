Apple, aple, appl. I understand they are the same word just a typo away. But how the heck does a computer also know that??


And honestly, I gave little to no thought to it until I needed it while building Fonli, my AI-powered language learning app. I wanted users to get credit when they typed an answer that was almost right — a tiny typo shouldn’t punish them.

Turns out this has a name: fuzzy search.

That sent me down the rabbit hole of typo-tolerant matching, and I quickly found out there are a few different ways to add it to an application:

- Levenshtein
- N-grams
- third-party libraries
- Elasticsearch

Each one comes with its own trade-offs around accuracy, speed, and how much complexity you’re willing to take on.

What surprised me most is how invisible fuzzy search has become. We see it on Instagram, Google Maps, and Amazon, and we just expect it everywhere. The moment a search returns “no results” after a single typo, the user is gone.

I broke down everything I learned in this carousel — the algorithms, the libraries, the trade-offs, and how to scale it.

How are you handling typos and misspellings in your own projects?
