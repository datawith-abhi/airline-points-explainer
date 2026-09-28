"""Copy a completed local character render into the repository hosting root."""
from pathlib import Path
import shutil
R=Path(__file__).parent
for name in ("airline-points-character.mp4", "presenter-poster.jpg"):
    source=R/"site"/name
    if source.exists(): shutil.copy2(source,R/name)
print("Static files ready. Deploy the latest commit in Render.")
