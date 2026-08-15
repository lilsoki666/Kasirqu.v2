import sqlite3
import os

class Database:
    def __init__(self, db_name="pos_store.db"):
        # PERBAIKAN PENTING: Penentuan jalur folder khusus penyimpanan data di Android
        try:
            from kivy.app import App
            app = App.get_running_app()
            if app and app.user_data_dir:
                self.db_path = os.path.join(app.user_data_dir, db_name)
            else:
                self.db_path = db_name
        except Exception:
            self.db_path = db_name

        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

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
                
                # Tabel Penjualan
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
                
                # Tabel Detail Penjualan
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
                
                # Tabel Pengaturan
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
                ''')
                conn.commit()
        except Exception as e:
            print(f"Error Init DB: {e}")

    # --- FUNGSI UNTUK DASHBOARD (Agar V1.0.0 Tidak Error) ---
    def get_today_summary(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        COALESCE(SUM(total_amount), 0) AS total_penjualan, 
                        COUNT(id) AS total_transaksi 
                    FROM sales 
                    WHERE DATE(created_at) = DATE('now', 'localtime')
                """)
                row = cursor.fetchone()
                return {
                    'total_sales': row[0] if row else 0,
                    'total_transactions': row[1] if row else 0
                }
        except Exception as e:
            print(f"Error Today Summary: {e}")
            return {'total_sales': 0, 'total_transactions': 0}

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
            print(f"Error Get Products: {e}")
            return []

    def add_product(self, name, price, stock):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
                conn.commit()
                return True
        except Exception:
            return False

    def update_product(self, prod_id, name, price, stock):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE products SET name=?, price=?, stock=? WHERE id=?", (name, price, stock, prod_id))
                conn.commit()
                return True
        except Exception:
            return False

    def delete_product(self, prod_id):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM products WHERE id=?", (prod_id,))
                conn.commit()
                return True
        except Exception:
            return False

    # --- TRANSAKSI ---
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
                return True, "Sukses"
        except Exception as e:
            return False, str(e)

    def get_sales(self):
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM sales ORDER BY id DESC")
                return [dict(row) for row in cursor.fetchall()]
        except Exception:
            return []

    def get_sale_items(self, sale_id):
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM sale_items WHERE sale_id=?", (sale_id,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception:
            return []

    # --- PENGATURAN ---
    def get_setting(self, key, default=""):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
                row = cursor.fetchone()
                return row[0] if row else default
        except Exception:
            return default

    def set_setting(self, key, value):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
                conn.commit()
                return True
        except Exception:
            return False
