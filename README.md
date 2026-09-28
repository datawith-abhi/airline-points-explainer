# The Points Economy

A 120-second, 16:9 explainer about the economics of airline loyalty programs, created for a free Render static site.

## Watch

Open `index.html` through a static HTTP server or use the deployed Render page. Download `airline-points.mp4` for the standalone 1920 × 1080 film. English captions are burned in; `subtitles.srt` is included separately.

## Creative treatment

Fourteen animated editorial scenes: photographic paper cutouts, layered entrances, moving points, money-flow diagrams, an animated headline statistic, highlighted captions, and original instrumental accompaniment. Narration uses the open Kokoro neural model's `af_heart` synthetic female voice. No presenter appears.

## Accuracy

The film distinguishes cash receipts from revenue and profit. Delta's $8.2 billion 2025 American Express remuneration is not presented as profit. The empty-seat example is illustrative. The film does not claim all airlines make more ticket revenue or more profit from points.

- https://ir.delta.com/news/news-details/2026/Delta-Air-Lines-Announces-December-Quarter-and-Full-Year-2025-Financial-Results/default.aspx
- https://www.sec.gov/Archives/edgar/data/27904/000002790426000013/dal-20251231.htm

## Credits

- Aircraft: Jeffry Surianto, Pexels photo 36219158, Pexels License.
- Groceries: SHVETS production, Pexels photo 8900041, Pexels License.
- Cabin: Alexander Schimmeck, Unsplash photo avvyNj7FWb8, Unsplash License.
- Kokoro model: hexgrad/Kokoro-82M, Apache 2.0. Kokoro ONNX wrapper: thewh1teagle/kokoro-onnx, MIT.
- Captions: Whisper word timestamps on the actual narration, checked against the script.

## Reproduce

Use Python 3.12. Run `python -m pip install --target deps -r renderer-requirements.txt`, then `fetch_assets.py`, `narrate.py 0.95`, `captions.py`, and `film.py`. Rendering is local; Render serves the completed film and page. Model weights, installed dependencies, and local authentication files are not included. The dependency list is named `renderer-requirements.txt` so static hosting does not install the narration tools.

## Render settings

Service type: Static Site. Branch: `main`. Build command: `echo Ready`. Publish directory: `.`. No environment variables or paid compute instance are required.
