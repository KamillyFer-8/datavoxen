from pathlib import Path
import sys

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'backend'))
from app.main import export_result
from app.simulation.engine import result

path=root/'docs/screenshots/relatorio-exemplo.pdf'
path.parent.mkdir(parents=True,exist_ok=True)
path.write_bytes(export_result(result(),'pdf','months').body)
print(path)
