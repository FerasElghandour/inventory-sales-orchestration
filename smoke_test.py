import sqlite3
from sales_core import SalesStore
store=SalesStore();store.set_stock('demo',10,125)
assert store.quote({'demo':3})['total_cents']==375
store.reserve('order-1',{'demo':3},'2024-01-01','2024-01-02')
assert store.db.execute("SELECT units FROM inventory").fetchone()[0]==7
for order,qty in [('oversell',8),('order-1',2)]:
    try:store.reserve(order,{'demo':qty},'2024-01-01','2024-01-02')
    except (ValueError,sqlite3.IntegrityError):pass
    else:raise AssertionError('Invalid reservation accepted')
assert store.db.execute('SELECT units FROM inventory').fetchone()[0]==7
assert store.db.execute('SELECT count(*) FROM orders').fetchone()[0]==1
try:store.reserve('backdate',{'demo':1},'2024-02-01','2024-01-01')
except ValueError:pass
else:raise AssertionError('Invalid deadline accepted')
store.close();print('Cent-based quotes, atomic reservation, oversell rejection, rollback, and deadlines passed.')
