Why does Instagram still find your friend when you misspell their name?


For a long time I just called it “smart search” and moved on.

Turns out it has a name: fuzzy search.

I ran into it while building Fonli, my AI-powered language learning app. I wanted users to get credit when they typed an answer that was almost right — a tiny typo shouldn’t punish them.

That sent me down the rabbit hole of typo-tolerant matching, and I had to wrap my head around a few things:
* how to actually measure similarity between two words
* which algorithm to pick (and why)
* whether to use a library or roll my own
* the trade-offs of being “too forgiving”
* how to keep it fast at scale

Honestly, the math behind it sounded scarier than it really is.

After a couple of hours I realized you don’t need to implement Levenshtein from scratch. There are battle-tested libraries — fuzzywuzzy in Python, Fuse.js in JavaScript — that hand you a similarity score out of the box.

What surprised me most is how invisible fuzzy search has become. We see it on Instagram, Google Maps, Amazon, and we just expect it everywhere. The moment a search returns “no results” after a single typo, the user is gone.

I broke down everything I learned in this carousel — the algorithms, the libraries, the trade-offs, and how to scale it.

How are you handling typos and misspellings in your own projects?
