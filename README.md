# The Points Economy — character edition

A two-minute explainer led by an original talking paper-cutout presenter. She holds the rewards card, points to the bank and airline, responds to the economics, and guides the viewer through grocery, cafe, bank, airport, and cabin scenes.

## Watch

https://airline-points-explainer.onrender.com/

The current film is `airline-points-character.mp4`: 1920 × 1080, 16:9, 30 fps, exactly 120 seconds, with music and burned-in English captions. `subtitles.srt` is also provided. The earlier `airline-points.mp4` is the previous collage edition.

## Animation

`puppet.py` is the original layered presenter rig. Her arms use inverse kinematics; poses follow authored performance beats. She has gaze shifts, blinking, head nods, weight shifts, and independently animated hands. Nine mouth shapes follow Rhubarb audio-derived speech cues in `mouth-cues.json`. The mouth rests during pauses.

`stage.py` builds the paper sets and props. `character_film.py` stages the host performance, animates transactions and demonstrations, changes camera framing, and burns the existing Whisper-aligned captions. The soundtrack remains the same female voice as the previous edition so the presenter speaks the familiar narration.

## Re-render on Windows

Use Python 3.12 and the standard Windows fonts. Install local rendering dependencies with:

```sh
python -m pip install --target deps -r renderer-requirements.txt
python fetch_assets.py
python film.py
python package.py
```

The exact soundtrack and mouth cues are included. `python character_film.py --sample` makes the opening performance preview; `--frames` makes a storyboard. To change the dialogue, regenerate the audio and captions, then run [Rhubarb Lip Sync](https://github.com/DanielSWolf/rhubarb-lip-sync) on `narration.wav` with `dialog.txt` to rebuild the mouth cues. Rhubarb is MIT licensed. Dependencies and model files are not committed.

## Factual sources

Partnership cash, revenue, and profit are different measures. The film does not claim every airline earns more revenue or profit from points than tickets. The empty-seat example is illustrative.

- [Delta 2025 financial results](https://ir.delta.com/news/news-details/2026/Delta-Air-Lines-Announces-December-Quarter-and-Full-Year-2025-Financial-Results/default.aspx): $8.2 billion of American Express partnership remuneration.
- [Delta 2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/27904/000002790426000013/dal-20251231.htm): loyalty accounting, deferred travel, and redemption estimates.

## Credits

Original presenter, paper-set illustrations, choreography, and music. Aircraft cutout: [Jeffry Surianto / Pexels](https://www.pexels.com/photo/white-airplane-taking-off-from-airport-runway-36219158/), Pexels License. Narration: Kokoro `af_heart` synthetic female voice (Kokoro-82M, Apache 2.0; Kokoro ONNX wrapper, MIT). Captions use Whisper timestamps on the actual narration. The asset preparation script also fetches the prior edition's unused groceries and cabin photographs, credited in its original repository history.

## Render

Free Static Site, branch `main`, build command `echo Ready`, publish directory `.`. No paid compute or environment variables are needed. The dependency file is intentionally named `renderer-requirements.txt` to prevent the static host from installing local narration dependencies. Deploy updated commits manually in Render.
