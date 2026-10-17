"""Offline example using the public implementation; see README for evidence scope."""
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
os.chdir(ROOT)

from sales_core import SalesStore
store=SalesStore()
store.set_stock('demo',10,125)
print(store.reserve('order-1',{'demo':3},'2024-01-01','2024-01-02'))
print({'stock_remaining':store.db.execute('SELECT units FROM inventory').fetchone()[0]})
store.close()
