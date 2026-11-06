# KET Word Review flashcards

Lives in the ket/ folder of studyenglishwithteacheredwin-tech/word-review (the Movers app stays at the root).
Live: https://studyenglishwithteacheredwin-tech.github.io/word-review/ket/
- index.html: the whole app (Learn / Listen / Spell / Test, 🐢 slow audio, IPA, progress saved on the phone).
- data/ket/uNN.json: one file per unit (words, Vietnamese, IPA, picture, normal + slow audio).
- sw.js (cache word-review-ket-vN; bump N when data changes) + manifest.json for offline use and "Add to Home Screen".
- export.py: rebuilds data/ from the KET book kit + audio.
