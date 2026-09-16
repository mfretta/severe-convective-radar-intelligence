"""Pre-render browser PPI overlays for every completed DBZH timestamp."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from sc_sentinel.serving.ppi import ensure_ppi
state=json.loads((ROOT/'data'/'gold'/'archive_tracks.json').read_text(encoding='utf-8'))
for index,token in enumerate(state['processed'],start=1):
    ensure_ppi(ROOT,token)
    print(f'{index}/{len(state["processed"])} {token}',flush=True)
