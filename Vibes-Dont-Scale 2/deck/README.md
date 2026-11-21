# Vibes Don't Scale: AI evals for secure LLM apps

A 34-slide HyperFrames slideshow for a 45-minute B.Tech talk (about 36 minutes of talk and demo, then Q&A).

## Present it

Requires Node.js 22 or newer. The first run downloads the HyperFrames CLI, so do it once before the talk.

```
npx --yes hyperframes@0.9.72 present .
```

- It opens a browser tab. Press **P** (or click Present) to open the **audience** window and put that window on the projector.
- Use **→ / Space** for next and **←** to go back. Slides with build-ups reveal one item per click.
- Speaker notes appear in the presenter view.
- Fonts and GSAP are bundled in `assets/`. Apart from the one-time CLI download above, the deck does not need the internet. The QR codes do need internet on the audience's phones.

Backup: `Vibes-Dont-Scale-slides.pdf` has the same slides as a PDF.

## Edit the slides

All slide text, speaker notes and QR links live in `tools/build_deck.py`. Styles live in `tools/deck.css`.

```
pip install qrcode
python3 tools/build_deck.py        # regenerates index.html
npx --yes hyperframes@0.9.72 check # optional: lint and layout check
```

Placeholders to fill: slide 1 (`[Your name] · [College / Event]`) and slide 2 (what you do, one AI thing you shipped).
