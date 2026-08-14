__version__ = "1.0.0"

import csv
import os
from datetime import datetime
import traceback

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from database import Database


KV = """
#:import dp kivy.metrics.dp

<NavButton@Button>:
    size_hint_x: None
    width: dp(112)
    size_hint_y: 1
    background_normal: ""
    background_color: .10,.13,.18,1
    color: .92,.95,1,1
    font_size: "13sp"
    bold: True

<TitleLabel@Label>:
    font_size: "23sp"
    bold: True
    color: .08,.10,.14,1
    size_hint_y: None
    height: dp(44)
    halign: "left"
    valign: "middle"
    text_size: self.size

<RootLayout>:
    orientation: "vertical"
    padding: 0
    spacing: 0
    canvas.before:
        Color:
            rgba: .94,.95,.97,1
        Rectangle:
            pos: self.pos
            size: self.size

    # HEADER
    BoxLayout:
        size_hint_y: None
        height: dp(62)
        padding: dp(14), dp(5)
        canvas.before:
            Color:
                rgba: .05,.07,.10,1
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: app.store_name
            font_size: "20sp"
            bold: True
            color: 1,1,1,1
            halign: "left"
            valign: "middle"
            text_size: self.size

        Label:
            text: "POS v" + app.version
            size_hint_x: None
            width: dp(82)
            font_size: "11sp"
            color: .70,.74,.82,1
            halign: "right"
            valign: "middle"
            text_size: self.size

    # MOBILE NAVIGATION - NO LEFT SIDEBAR
    BoxLayout:
        size_hint_y: None
        height: dp(58)
        padding: dp(5), dp(5)
        spacing: dp(5)
        canvas.before:
            Color:
                rgba: .10,.12,.16,1
            Rectangle:
                pos: self.pos
                size: self.size

        NavButton:
            text: "Dashboard"
            on_release: app.show_screen("dashboard")
        NavButton:
            text: "Kasir"
            on_release: app.show_screen("pos")
        NavButton:
            text: "Produk"
            on_release: app.show_screen("products")
        NavButton:
            text: "Riwayat"
            on_release: app.show_screen("history")
        NavButton:
            text: "Laporan"
            on_release: app.show_screen("reports")
        NavButton:
            text: "Pengaturan"
            on_release: app.show_screen("settings")

    ScreenManager:
        id: sm

        # DASHBOARD
        Screen:
            name: "dashboard"
            ScrollView:
                do_scroll_x: False
                BoxLayout:
                    orientation: "vertical"
                    padding: dp(16)
                    spacing: dp(10)
                    size_hint_y: None
                    height: self.minimum_height

                    TitleLabel:
                        text: "Dashboard"

                    Label:
                        text: "Ringkasan aktivitas toko"
                        size_hint_y: None
                        height: dp(25)
                        color: .43,.47,.54,1
                        halign: "left"
                        text_size: self.size

                    GridLayout:
                        cols: 1
                        spacing: dp(10)
                        size_hint_y: None
                        height: dp(380)

                        BoxLayout:
                            orientation: "vertical"
                            padding: dp(15)
                            canvas.before:
                                Color:
                                    rgba: 1,1,1,1
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [dp(12),dp(12),dp(12),dp(12)]
                            Label:
                                text: "PENJUALAN HARI INI"
                                font_size: "11sp"
                                bold: True
                                color: .43,.47,.54,1
                                halign: "left"
                                text_size: self.size
                            Label:
                                id: dash_sales
                                text: "Rp 0"
                                font_size: "24sp"
                                bold: True
                                color: .08,.40,.24,1
                                halign: "left"
                                text_size: self.size

                        BoxLayout:
                            orientation: "vertical"
                            padding: dp(15)
                            canvas.before:
                                Color:
                                    rgba: 1,1,1,1
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [dp(12),dp(12),dp(12),dp(12)]
                            Label:
                                text: "TRANSAKSI"
                                font_size: "11sp"
                                bold: True
                                color: .43,.47,.54,1
                                halign: "left"
                                text_size: self.size
                            Label:
                                id: dash_trx
                                text: "0"
                                font_size: "24sp"
                                bold: True
                                halign: "left"
                                text_size: self.size

                        BoxLayout:
                            orientation: "vertical"
                            padding: dp(15)
                            canvas.before:
                                Color:
                                    rgba: 1,1,1,1
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [dp(12),dp(12),dp(12),dp(12)]
                            Label:
                                text: "PRODUK AKTIF"
                                font_size: "11sp"
                                bold: True
                                color: .43,.47,.54,1
                                halign: "left"
                                text_size: self.size
                            Label:
                                id: dash_products
                                text: "0"
                                font_size: "24sp"
                                bold: True
                                halign: "left"
                                text_size: self.size

                        BoxLayout:
                            orientation: "vertical"
                            padding: dp(15)
                            canvas.before:
                                Color:
                                    rgba: 1,1,1,1
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [dp(12),dp(12),dp(12),dp(12)]
                            Label:
                                text: "STOK MENIPIS"
                                font_size: "11sp"
                                bold: True
                                color: .43,.47,.54,1
                                halign: "left"
                                text_size: self.size
                            Label:
                                id: dash_low
                                text: "0"
                                font_size: "24sp"
                                bold: True
                                color: .68,.28,.08,1
                                halign: "left"
                                text_size: self.size

                    Button:
                        text: "REFRESH DASHBOARD"
                        size_hint_y: None
                        height: dp(50)
                        background_normal: ""
                        background_color: .10,.13,.18,1
                        color: 1,1,1,1
                        bold: True
                        on_release: app.refresh_all()

        # POS - PORTRAIT FIRST
        Screen:
            name: "pos"
            BoxLayout:
                orientation: "vertical"
                padding: dp(10)
                spacing: dp(9)

                # PRODUCTS
                BoxLayout:
                    orientation: "vertical"
                    size_hint_y: .47
                    spacing: dp(7)

                    Label:
                        text: "PILIH PRODUK"
                        size_hint_y: None
                        height: dp(34)
                        font_size: "17sp"
                        bold: True
                        color: .08,.10,.14,1
                        halign: "left"
                        text_size: self.size

                    TextInput:
                        id: search_pos
                        hint_text: "Cari nama produk / barcode..."
                        multiline: False
                        size_hint_y: None
                        height: dp(48)
                        padding: dp(12), dp(11)
                        font_size: "14sp"
                        on_text: app.refresh_pos_products(self.text)

                    ScrollView:
                        do_scroll_x: False
                        GridLayout:
                            id: product_grid
                            cols: 1
                            spacing: dp(7)
                            padding: dp(1)
                            size_hint_y: None
                            height: self.minimum_height

                # CART
                BoxLayout:
                    orientation: "vertical"
                    size_hint_y: .53
                    padding: dp(11)
                    spacing: dp(7)
                    canvas.before:
                        Color:
                            rgba: 1,1,1,1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(12),dp(12),dp(12),dp(12)]

                    Label:
                        text: "KERANJANG BELANJA"
                        size_hint_y: None
                        height: dp(32)
                        font_size: "16sp"
                        bold: True
                        color: .08,.10,.14,1
                        halign: "left"
                        text_size: self.size

                    ScrollView:
                        do_scroll_x: False
                        GridLayout:
                            id: cart_grid
                            cols: 1
                            spacing: dp(5)
                            size_hint_y: None
                            height: self.minimum_height

                    GridLayout:
                        cols: 2
                        spacing: dp(5)
                        size_hint_y: None
                        height: dp(105)

                        Label:
                            text: "Subtotal"
                            halign: "left"
                            text_size: self.size
                        Label:
                            id: pos_subtotal
                            text: "Rp 0"
                            bold: True
                            halign: "right"
                            text_size: self.size

                        Label:
                            text: "Diskon"
                            halign: "left"
                            text_size: self.size
                        TextInput:
                            id: discount_input
                            text: "0"
                            input_filter: "float"
                            multiline: False
                            on_text: app.recalculate_pos()

                        Label:
                            text: "TOTAL"
                            bold: True
                            font_size: "16sp"
                            halign: "left"
                            text_size: self.size
                        Label:
                            id: pos_total
                            text: "Rp 0"
                            bold: True
                            font_size: "18sp"
                            halign: "right"
                            text_size: self.size

                    GridLayout:
                        cols: 2
                        spacing: dp(5)
                        size_hint_y: None
                        height: dp(82)

                        TextInput:
                            id: paid_input
                            hint_text: "Uang dibayar"
                            input_filter: "float"
                            multiline: False
                            on_text: app.recalculate_pos()

                        Spinner:
                            id: payment_spinner
                            text: "Tunai"
                            values: ["Tunai","QRIS","Transfer","Debit/Kredit"]

                        Label:
                            text: "Kembalian"
                            bold: True
                            halign: "left"
                            text_size: self.size
                        Label:
                            id: change_label
                            text: "Rp 0"
                            bold: True
                            halign: "right"
                            text_size: self.size

                    Button:
                        text: "PROSES PEMBAYARAN"
                        size_hint_y: None
                        height: dp(52)
                        background_normal: ""
                        background_color: .07,.45,.27,1
                        color: 1,1,1,1
                        bold: True
                        font_size: "15sp"
                        on_release: app.checkout()

        # PRODUCTS
        Screen:
            name: "products"
            BoxLayout:
                orientation: "vertical"
                padding: dp(14)
                spacing: dp(8)

                TitleLabel:
                    text: "Produk"

                BoxLayout:
                    size_hint_y: None
                    height: dp(48)
                    spacing: dp(6)

                    TextInput:
                        id: search_product
                        hint_text: "Cari produk..."
                        multiline: False
                        padding: dp(11),dp(11)
                        on_text: app.refresh_products(self.text)

                    Button:
                        text: "+ PRODUK"
                        size_hint_x: None
                        width: dp(102)
                        background_normal: ""
                        background_color: .07,.45,.27,1
                        color: 1,1,1,1
                        bold: True
                        on_release: app.product_form()

                Button:
                    text: "+ KATEGORI"
                    size_hint_y: None
                    height: dp(44)
                    background_normal: ""
                    background_color: .10,.13,.18,1
                    color: 1,1,1,1
                    bold: True
                    on_release: app.category_form()

                ScrollView:
                    do_scroll_x: False
                    GridLayout:
                        id: products_grid
                        cols: 1
                        spacing: dp(7)
                        size_hint_y: None
                        height: self.minimum_height

        # HISTORY
        Screen:
            name: "history"
            BoxLayout:
                orientation: "vertical"
                padding: dp(14)
                spacing: dp(7)

                TitleLabel:
                    text: "Riwayat Transaksi"

                ScrollView:
                    do_scroll_x: False
                    GridLayout:
                        id: history_grid
                        cols: 1
                        spacing: dp(7)
                        size_hint_y: None
                        height: self.minimum_height

        # REPORTS
        Screen:
            name: "reports"
            BoxLayout:
                orientation: "vertical"
                padding: dp(14)
                spacing: dp(7)

                TitleLabel:
                    text: "Laporan 30 Hari"

                ScrollView:
                    do_scroll_x: False
                    GridLayout:
                        id: report_grid
                        cols: 1
                        spacing: dp(7)
                        size_hint_y: None
                        height: self.minimum_height

                Button:
                    text: "EXPORT CSV"
                    size_hint_y: None
                    height: dp(50)
                    background_normal: ""
                    background_color: .10,.13,.18,1
                    color: 1,1,1,1
                    bold: True
                    on_release: app.export_csv()

        # SETTINGS
        Screen:
            name: "settings"
            ScrollView:
                do_scroll_x: False
                BoxLayout:
                    orientation: "vertical"
                    padding: dp(16)
                    spacing: dp(9)
                    size_hint_y: None
                    height: self.minimum_height

                    TitleLabel:
                        text: "Pengaturan"

                    TextInput:
                        id: setting_store
                        hint_text: "Nama toko"
                        text: app.store_name
                        multiline: False
                        size_hint_y: None
                        height: dp(48)
                        padding: dp(12),dp(12)

                    TextInput:
                        id: setting_address
                        hint_text: "Alamat"
                        text: app.store_address
                        multiline: False
                        size_hint_y: None
                        height: dp(48)
                        padding: dp(12),dp(12)

                    TextInput:
                        id: setting_tax
                        hint_text: "Pajak (%)"
                        text: app.tax_percent
                        input_filter: "float"
                        multiline: False
                        size_hint_y: None
                        height: dp(48)
                        padding: dp(12),dp(12)

                    TextInput:
                        id: setting_cashier
                        hint_text: "Nama kasir"
                        text: app.cashier_name
                        multiline: False
                        size_hint_y: None
                        height: dp(48)
                        padding: dp(12),dp(12)

                    Button:
                        text: "SIMPAN PENGATURAN"
                        size_hint_y: None
                        height: dp(50)
                        background_normal: ""
                        background_color: .07,.45,.27,1
                        color: 1,1,1,1
                        bold: True
                        on_release: app.save_settings()

                    Button:
                        text: "BUAT BACKUP DATABASE"
                        size_hint_y: None
                        height: dp(50)
                        background_normal: ""
                        background_color: .10,.13,.18,1
                        color: 1,1,1,1
                        bold: True
                        on_release: app.make_backup()

                    Label:
                        text: "Database SQLite lokal; aplikasi dapat berjalan offline."
                        size_hint_y: None
                        height: dp(40)
                        color: .43,.47,.54,1
                        halign: "left"
                        text_size: self.size
"""




class RootLayout(BoxLayout):
    pass


class POSApp(App):
    version = __version__
    store_name = StringProperty("TOKO SAYA")
    store_address = StringProperty("")
    tax_percent = StringProperty("0")
    cashier_name = StringProperty("Admin")

    def build(self):
        # Keep build() lightweight. Kivy assigns self.root only after
        # build() returns, so UI refreshes must not happen here.
        self.title = "POS Kasir"
        self.db = Database(os.path.join(self.user_data_dir, "pos.db"))
        self.load_settings()
        self.cart = []
        Builder.load_string(KV)
        return RootLayout()

    def on_start(self):
        # Run after Kivy has assigned self.root.
        try:
            self.refresh_all()
        except Exception:
            self.log_startup_error()
            self.show_startup_error()

    def log_startup_error(self):
        try:
            path = os.path.join(self.user_data_dir, "startup_error.log")
            with open(path, "a", encoding="utf-8") as f:
                f.write("\n=== POS KASIR STARTUP ERROR ===\n")
                f.write(traceback.format_exc())
        except Exception:
            pass

    def show_startup_error(self):
        message = (
            "Aplikasi berhasil dibuka, tetapi terjadi kesalahan saat "
            "memuat data awal.\n\n"
            "Silakan periksa file startup_error.log di folder data aplikasi."
        )
        Clock.schedule_once(lambda dt: self.info(message, "Kesalahan Startup"), 0)

    def load_settings(self):
        self.store_name = self.db.get_setting("store_name", "TOKO SAYA")
        self.store_address = self.db.get_setting("store_address", "")
        self.tax_percent = self.db.get_setting("tax_percent", "0")
        self.cashier_name = self.db.get_setting("cashier_name", "Admin")

    def show_screen(self, name):
        self.root.ids.sm.current = name
        if name == "dashboard":
            self.refresh_dashboard()
        elif name == "pos":
            self.refresh_pos_products("")
            self.refresh_cart()
        elif name == "products":
            self.refresh_products("")
        elif name == "history":
            self.refresh_history()
        elif name == "reports":
            self.refresh_reports()

    def refresh_all(self):
        self.refresh_dashboard()
        self.refresh_pos_products("")
        self.refresh_cart()
        self.refresh_products("")
        self.refresh_history()
        self.refresh_reports()

    @staticmethod
    def money(value):
        return "Rp {:,.0f}".format(float(value)).replace(",", ".")

    def refresh_dashboard(self):
        s, product_count, low = self.db.summary_today()
        self.root.ids.dash_sales.text = f"Penjualan hari ini: {self.money(s['total'])}"
        self.root.ids.dash_trx.text = f"Transaksi: {s['transactions']}"
        self.root.ids.dash_products.text = f"Produk aktif: {product_count}"
        self.root.ids.dash_low.text = f"Stok menipis: {low}"

    def refresh_pos_products(self, search):
        grid = self.root.ids.product_grid
        grid.clear_widgets()
        for p in self.db.products(search)[:100]:
            b = Button(
                text=f"{p['name']}\nStok {p['stock']:g}  â€¢  {self.money(p['sell_price'])}",
                size_hint_y=None, height=dp(62),
                font_size="14sp",
                halign="left",
                valign="middle",
                text_size=(None, None)
            )
            b.bind(on_release=lambda btn, pid=p["id"]: self.add_to_cart(pid))
            grid.add_widget(b)

    def add_to_cart(self, product_id):
        p = self.db.product_by_id(product_id)
        if not p or p["stock"] <= 0:
            self.info("Stok produk habis.")
            return
        for item in self.cart:
            if item["id"] == product_id:
                if item["qty"] + 1 > p["stock"]:
                    self.info("Jumlah melebihi stok.")
                    return
                item["qty"] += 1
                item["line_total"] = item["qty"] * item["price"]
                self.refresh_cart()
                return
        self.cart.append({
            "id": p["id"], "name": p["name"], "qty": 1,
            "price": float(p["sell_price"]), "discount": 0,
            "line_total": float(p["sell_price"])
        })
        self.refresh_cart()

    def refresh_cart(self):
        grid = self.root.ids.cart_grid
        grid.clear_widgets()
        for item in self.cart:
            row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(4))
            label = Label(
                text=f"{item['name']} x{item['qty']:g}\n{self.money(item['line_total'])}",
                halign="left"
            )
            minus = Button(text="-", size_hint_x=None, width=dp(42))
            plus = Button(text="+", size_hint_x=None, width=dp(42))
            delete = Button(text="X", size_hint_x=None, width=dp(42))
            minus.bind(on_release=lambda btn, iid=item["id"]: self.change_qty(iid, -1))
            plus.bind(on_release=lambda btn, iid=item["id"]: self.change_qty(iid, 1))
            delete.bind(on_release=lambda btn, iid=item["id"]: self.remove_cart(iid))
            row.add_widget(label)
            row.add_widget(minus)
            row.add_widget(plus)
            row.add_widget(delete)
            grid.add_widget(row)
        self.recalculate_pos()

    def change_qty(self, product_id, delta):
        for item in self.cart:
            if item["id"] == product_id:
                p = self.db.product_by_id(product_id)
                item["qty"] += delta
                if item["qty"] <= 0:
                    self.remove_cart(product_id)
                    return
                if item["qty"] > p["stock"]:
                    item["qty"] = p["stock"]
                item["line_total"] = item["qty"] * item["price"]
                break
        self.refresh_cart()

    def remove_cart(self, product_id):
        self.cart = [x for x in self.cart if x["id"] != product_id]
        self.refresh_cart()

    def recalculate_pos(self, *_):
        if not hasattr(self, "root") or not self.root:
            return
        subtotal = sum(x["line_total"] for x in self.cart)
        try:
            discount = max(0, float(self.root.ids.discount_input.text or 0))
        except ValueError:
            discount = 0
        try:
            tax = max(0, float(self.tax_percent)) / 100 * max(0, subtotal - discount)
        except ValueError:
            tax = 0
        total = max(0, subtotal - discount + tax)
        try:
            paid = max(0, float(self.root.ids.paid_input.text or 0))
        except ValueError:
            paid = 0
        change = max(0, paid - total)
        self.root.ids.pos_subtotal.text = self.money(subtotal)
        self.root.ids.pos_total.text = self.money(total)
        self.root.ids.change_label.text = self.money(change)
        return subtotal, discount, tax, total, paid, change

    def checkout(self):
        if not self.cart:
            self.info("Keranjang masih kosong.")
            return
        subtotal, discount, tax, total, paid, change = self.recalculate_pos()
        payment = self.root.ids.payment_spinner.text
        if payment == "Tunai" and paid < total:
            self.info("Uang dibayar belum cukup.")
            return
        if payment != "Tunai":
            paid = total
            change = 0
        invoice = self.db.save_sale(
            self.cart, subtotal, discount, tax, total, paid, change, payment
        )
        self.cart = []
        self.root.ids.discount_input.text = "0"
        self.root.ids.paid_input.text = ""
        self.refresh_all()
        self.info(
            f"Transaksi berhasil.\n{invoice}\nTotal: {self.money(total)}"
        )

    def refresh_products(self, search):
        grid = self.root.ids.products_grid
        grid.clear_widgets()
        for p in self.db.products(search):
            row = BoxLayout(size_hint_y=None, height=dp(68), spacing=dp(5))
            row.add_widget(Label(
                text=f"{p['name']} | {p['barcode'] or '-'}\n"
                     f"Jual {self.money(p['sell_price'])} | Stok {p['stock']:g} {p['unit']}",
                halign="left",
                valign="middle",
                text_size=(None, None)
            ))
            edit = Button(text="Edit", size_hint_x=None, width=dp(70))
            delete = Button(text="Hapus", size_hint_x=None, width=dp(70))
            edit.bind(on_release=lambda btn, pid=p["id"]: self.product_form(pid))
            delete.bind(on_release=lambda btn, pid=p["id"]: self.delete_product(pid))
            row.add_widget(edit)
            row.add_widget(delete)
            grid.add_widget(row)

    def product_form(self, product_id=None):
        p = self.db.product_by_id(product_id) if product_id else None
        box = BoxLayout(orientation="vertical", spacing=dp(6), padding=dp(8))
        fields = {}
        for key, hint in [
            ("barcode", "Barcode (opsional)"),
            ("name", "Nama produk"),
            ("buy_price", "Harga beli"),
            ("sell_price", "Harga jual"),
            ("stock", "Stok"),
            ("unit", "Satuan"),
            ("min_stock", "Batas stok minimum"),
        ]:
            t = TextInput(
                hint_text=hint, multiline=False,
                size_hint_y=None, height=dp(40),
                text="" if not p else str(p[key] if p[key] is not None else "")
            )
            fields[key] = t
            box.add_widget(t)

        categories = self.db.categories()
        cat_names = [c["name"] for c in categories]
        current_cat = "Umum"
        if p and p["category_id"]:
            for c in categories:
                if c["id"] == p["category_id"]:
                    current_cat = c["name"]
                    break

        cat_spinner = Spinner(
            text=current_cat, values=cat_names,
            size_hint_y=None, height=dp(40)
        )
        box.add_widget(cat_spinner)

        save = Button(text="Simpan", size_hint_y=None, height=dp(44))
        box.add_widget(save)
        popup = Popup(title="Produk", content=box, size_hint=(.9, .9))

        def save_it(*_):
            try:
                cat = next(c for c in categories if c["name"] == cat_spinner.text)
                data = {
                    "id": product_id,
                    "barcode": fields["barcode"].text.strip(),
                    "name": fields["name"].text.strip(),
                    "category_id": cat["id"],
                    "buy_price": float(fields["buy_price"].text or 0),
                    "sell_price": float(fields["sell_price"].text or 0),
                    "stock": float(fields["stock"].text or 0),
                    "unit": fields["unit"].text.strip() or "pcs",
                    "min_stock": float(fields["min_stock"].text or 0),
                }
                if not data["name"] or data["sell_price"] < 0:
                    raise ValueError
                self.db.save_product(data)
                popup.dismiss()
                self.refresh_all()
            except Exception:
                self.info("Data tidak valid atau barcode sudah digunakan.")

        save.bind(on_release=save_it)
        popup.open()

    def delete_product(self, product_id):
        self.db.delete_product(product_id)
        self.refresh_all()

    def category_form(self):
        box = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(8))
        t = TextInput(
            hint_text="Nama kategori", multiline=False,
            size_hint_y=None, height=dp(42)
        )
        b = Button(text="Simpan", size_hint_y=None, height=dp(44))
        box.add_widget(t)
        box.add_widget(b)
        popup = Popup(title="Kategori", content=box, size_hint=(.8, .35))

        def save_cat(*_):
            self.db.add_category(t.text)
            popup.dismiss()
            self.refresh_all()

        b.bind(on_release=save_cat)
        popup.open()

    def refresh_history(self):
        grid = self.root.ids.history_grid
        grid.clear_widgets()
        for s in self.db.sales(100):
            row = BoxLayout(size_hint_y=None, height=dp(58))
            row.add_widget(Label(
                text=f"{s['invoice']} | {s['created_at'].replace('T',' ')}\n"
                     f"{s['payment_method']} | {self.money(s['total'])}",
                halign="left"
            ))
            b = Button(text="Detail", size_hint_x=None, width=dp(80))
            b.bind(on_release=lambda btn, sid=s["id"]: self.show_sale(sid))
            row.add_widget(b)
            grid.add_widget(row)

    def show_sale(self, sale_id):
        sale = None
        for x in self.db.sales(200):
            if x["id"] == sale_id:
                sale = x
                break
        if not sale:
            return
        lines = [
            f"Invoice: {sale['invoice']}",
            f"Tanggal: {sale['created_at'].replace('T',' ')}",
            ""
        ]
        for item in self.db.sale_items(sale_id):
            lines.append(
                f"{item['product_name']} x{item['qty']:g} = "
                f"{self.money(item['line_total'])}"
            )
        lines += [
            "",
            f"Subtotal: {self.money(sale['subtotal'])}",
            f"Diskon: {self.money(sale['discount'])}",
            f"Pajak: {self.money(sale['tax'])}",
            f"TOTAL: {self.money(sale['total'])}",
            f"Bayar: {self.money(sale['paid'])}",
            f"Kembali: {self.money(sale['change_amount'])}",
        ]
        self.info("\n".join(lines), "Detail Transaksi")

    def refresh_reports(self):
        grid = self.root.ids.report_grid
        grid.clear_widgets()
        rows = self.db.sales_report(30)
        if not rows:
            grid.add_widget(Label(
                text="Belum ada transaksi.",
                size_hint_y=None, height=dp(40)
            ))
            return
        for r in rows:
            grid.add_widget(Label(
                text=f"{r['day']} | {r['transactions']} transaksi | "
                     f"Total {self.money(r['total'])}",
                size_hint_y=None, height=dp(42), halign="left"
            ))

    def export_csv(self):
        path = os.path.join(self.user_data_dir, "laporan_30_hari.csv")
        rows = self.db.sales_report(30)
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Tanggal", "Transaksi", "Subtotal",
                "Diskon", "Pajak", "Total"
            ])
            for r in rows:
                writer.writerow([
                    r["day"], r["transactions"], r["subtotal"],
                    r["discount"], r["tax"], r["total"]
                ])
        self.info(f"CSV tersimpan di:\n{path}")

    def save_settings(self):
        ids = self.root.ids
        self.db.set_setting(
            "store_name", ids.setting_store.text.strip() or "TOKO SAYA"
        )
        self.db.set_setting("store_address", ids.setting_address.text.strip())
        self.db.set_setting("tax_percent", ids.setting_tax.text.strip() or "0")
        self.db.set_setting(
            "cashier_name", ids.setting_cashier.text.strip() or "Admin"
        )
        self.load_settings()
        self.refresh_all()
        self.info("Pengaturan disimpan.")

    def make_backup(self):
        filename = f"backup_pos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        path = os.path.join(self.user_data_dir, filename)
        self.db.backup(path)
        self.info(f"Backup dibuat di:\n{path}")

    def info(self, message, title="Informasi"):
        Popup(
            title=title,
            content=Label(text=message, halign="center", valign="middle"),
            size_hint=(.88, .55)
        ).open()


if __name__ == "__main__":
    POSApp().run()
