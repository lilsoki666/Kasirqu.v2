import sqlite3
import os
import sys

class Database:
    def __init__(self, db_name="pos_store.db"):
        # Menyimpan database di lokasi storage internal Android yang aman
        if 'PYTHON_EGG_CACHE' in os.environ:
            base_dir = os.environ.get('ANDROID_PRIVATE', os.path.dirname(__file__))
            self.db_name = os.path.join(base_dir, db_name)
        else:
            self.db_name = db_name
            
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        try:
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
                
                # Tabel Penjualan / Transaksi
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
                
                # Tabel Detail Item Penjualan
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
        except Exception as e:
            self.log_error(f"Error init_db: {str(e)}")

    def log_error(self, message):
        try:
            with open("startup_error.log", "a") as f:
                f.write(f"{message}\n")
        except:
            pass

    # --- CRUD PRODUK ---
    def get_products(self, query=""):
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                if query.strip():
                    cursor.execute("SELECT * FROM products WHERE name LIKE ? ORDER BY name ASC", (f"%{query}%",))
                else:
                    cursor.execute("SELECT * FROM products ORDER BY name ASC")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.log_error(f"Error get_products: {str(e)}")
            return []

    def add_product(self, name, price, stock):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
                conn.commit()
                return True
        except Exception as e:
            self.log_error(f"Error add_product: {str(e)}")
            return False

    def update_product(self, prod_id, name, price, stock):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE products SET name=?, price=?, stock=? WHERE id=?", (name, price, stock, prod_id))
                conn.commit()
                return True
        except Exception as e:
            self.log_error(f"Error update_product: {str(e)}")
            return False

    def delete_product(self, prod_id):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM products WHERE id=?", (prod_id,))
                conn.commit()
                return True
        except Exception as e:
            self.log_error(f"Error delete_product: {str(e)}")
            return False

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
                    cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (item['qty'], item['id']))
                
                conn.commit()
                return True, "Transaksi Berhasil"
        except Exception as e:
            self.log_error(f"Error add_sale: {str(e)}")
            return False, str(e)

    def get_sales(self):
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM sales ORDER BY id DESC")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.log_error(f"Error get_sales: {str(e)}")
            return []

    def get_sale_items(self, sale_id):
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM sale_items WHERE sale_id=?", (sale_id,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.log_error(f"Error get_sale_items: {str(e)}")
            return []

    # --- DASHBOARD & SUMMARY ---
    def get_today_summary(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COALESCE(SUM(total_amount), 0), COUNT(id) 
                    FROM sales 
                    WHERE DATE(created_at) = DATE('now', 'localtime')
                """)
                row = cursor.fetchone()
                return {'total_sales': row[0], 'total_transactions': row[1]}
        except Exception as e:
            self.log_error(f"Error get_today_summary: {str(e)}")
            return {'total_sales': 0, 'total_transactions': 0}

    # --- PENGATURAN ---
    def get_setting(self, key, default=""):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
                row = cursor.fetchone()
                return row[0] if row else default
        except Exception as e:
            self.log_error(f"Error get_setting: {str(e)}")
            return default

    def set_setting(self, key, value):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
                conn.commit()
                return True
        except Exception as e:
            self.log_error(f"Error set_setting: {str(e)}")
            return False
