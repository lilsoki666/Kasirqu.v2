import sqlite3
import os

class Database:
    def __init__(self, db_name="pos_store.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabel Produk
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    stock INTEGER NOT NULL
                )
            ''')
            
            # Tabel Transaksi
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_no TEXT NOT NULL UNIQUE,
                    total_amount REAL NOT NULL,
                    paid_amount REAL NOT NULL,
                    change_amount REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabel Detail Transaksi
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sale_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_id INTEGER NOT NULL,
                    product_name TEXT NOT NULL,
                    price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    subtotal REAL NOT NULL,
                    FOREIGN KEY (sale_id) REFERENCES sales (id)
                )
            ''')
            
            # Tabel Pengaturan Toko
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            conn.commit()

    # --- CRUD PRODUK ---
    def get_products(self, query=""):
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if query.strip():
                cursor.execute("SELECT * FROM products WHERE name LIKE ? ORDER BY name ASC", (f"%{query}%",))
            else:
                cursor.execute("SELECT * FROM products ORDER BY name ASC")
            return [dict(row) for row in cursor.fetchall()]

    def add_product(self, name, price, stock):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
            conn.commit()

    def update_product(self, prod_id, name, price, stock):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE products SET name=?, price=?, stock=? WHERE id=?", (name, price, stock, prod_id))
            conn.commit()

    def delete_product(self, prod_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id=?", (prod_id,))
            conn.commit()

    # --- TRANSAKSI & PENJUALAN ---
    def add_sale(self, invoice_no, cart_items, total, paid, change):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO sales (invoice_no, total_amount, paid_amount, change_amount) VALUES (?, ?, ?, ?)",
                    (invoice_no, total, paid, change)
                )
                sale_id = cursor.lastrowid

                for item in cart_items:
                    cursor.execute(
                        "INSERT INTO sale_items (sale_id, product_name, price, quantity, subtotal) VALUES (?, ?, ?, ?, ?)",
                        (sale_id, item['name'], item['price'], item['qty'], item['line_total'])
                    )
                    # Potong Stok Produk
                    cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (item['qty'], item['id']))
                
                conn.commit()
                return True, "Transaksi Berhasil"
        except Exception as e:
            return False, str(e)

    def get_sales(self):
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sales ORDER BY id DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_sale_items(self, sale_id):
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sale_items WHERE sale_id=?", (sale_id,))
            return [dict(row) for row in cursor.fetchall()]

    # --- PENGATURAN ---
    def get_setting(self, key, default=""):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
            row = cursor.fetchone()
            return row[0] if row else default

    def set_setting(self, key, value):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
            conn.commit()
