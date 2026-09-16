from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from sc_sentinel.hazards.scoring import score_cell  # noqa: E402
if __name__ == "__main__":
    token=sys.argv[1] if len(sys.argv)>1 else "2026083023540400"
    p=ROOT/'data'/'gold'/'cells'/f'time={token}.json'; d=json.loads(p.read_text(encoding='utf-8'))
    for cell in d['cells']: cell['hazards']=score_cell(cell)
    p.write_text(json.dumps(d,indent=2),encoding='utf-8')
    print(f"scored={len(d['cells'])}")
