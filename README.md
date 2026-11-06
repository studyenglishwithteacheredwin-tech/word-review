# Word Review flashcards (Movers)

Static web app: open index.html on any web host (GitHub Pages).
- index.html — the whole app (Learn / Listen & pick / Test), progress saved on the phone.
- data/movers/uNN.json — one file per unit: words, Vietnamese, tricky part, picture and audio.
- sw.js + manifest.json — offline cache and "Add to Home Screen".
- export.py — rebuilds data/ from the Movers book kit + audio (run again after any word or picture change).
To add Starters / Flyers / KET later: export to data/<level>/ and add a level picker.
