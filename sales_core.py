"""Atomic stock reservation and integer-cent quoting for a sales workflow."""
import sqlite3
from datetime import date

class SalesStore:
    def __init__(self,path=':memory:'):
        self.db=sqlite3.connect(path,isolation_level=None)
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('CREATE TABLE IF NOT EXISTS inventory(sku TEXT PRIMARY KEY, units INTEGER NOT NULL CHECK(units>=0), price_cents INTEGER NOT NULL CHECK(price_cents>=0));\nCREATE TABLE IF NOT EXISTS orders(order_id TEXT PRIMARY KEY, requested_on TEXT NOT NULL, deadline TEXT NOT NULL, total_cents INTEGER NOT NULL);\nCREATE TABLE IF NOT EXISTS order_lines(order_id TEXT REFERENCES orders(order_id),sku TEXT REFERENCES inventory(sku),units INTEGER NOT NULL CHECK(units>0),PRIMARY KEY(order_id,sku));')
    def set_stock(self,sku,units,price_cents):
        if type(units) is not int or units<0 or type(price_cents) is not int or price_cents<0:raise ValueError('Nonnegative integer stock and prices required')
        self.db.execute('INSERT INTO inventory VALUES (?,?,?) ON CONFLICT(sku) DO UPDATE SET units=excluded.units,price_cents=excluded.price_cents',(sku,units,price_cents))
    def quote(self,items):
        if not items:raise ValueError('At least one item required')
        total=0
        for sku,qty in items.items():
            if type(qty) is not int or qty<=0:raise ValueError('Positive integer quantities required')
            row=self.db.execute('SELECT units,price_cents FROM inventory WHERE sku=?',(sku,)).fetchone()
            if row is None or row[0]<qty:raise ValueError('Unknown product or insufficient stock')
            total+=qty*row[1]
        return {'total_cents':total,'items':dict(items)}
    def reserve(self,order_id,items,requested_on,deadline):
        if not isinstance(order_id,str) or not order_id.strip():raise ValueError('Nonempty order ID required')
        if date.fromisoformat(deadline)<date.fromisoformat(requested_on):raise ValueError('Deadline precedes request date')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            quote=self.quote(items)
            self.db.execute('INSERT INTO orders VALUES (?,?,?,?)',(order_id,requested_on,deadline,quote['total_cents']))
            for sku,qty in items.items():
                changed=self.db.execute('UPDATE inventory SET units=units-? WHERE sku=? AND units>=?',(qty,sku,qty)).rowcount
                if changed!=1:raise ValueError('Stock changed during reservation')
                self.db.execute('INSERT INTO order_lines VALUES (?,?,?)',(order_id,sku,qty))
            self.db.execute('COMMIT');return quote
        except Exception:
            self.db.execute('ROLLBACK');raise
    def close(self):self.db.close()
