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
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from database import Database


KV = """
#:import dp kivy.metrics.dp

# --- Style Komponen Minimalis ---
<NavButton@Button>:
    size_hint_y: 1
    background_normal: ""
    background_color: (0.98, 0.98, 0.99, 1) if self.state == 'normal' else (0.90, 0.93, 0.98, 1)
    color: (.15, .20, .30, 1)
    font_size: "11sp"
    bold: True
    halign: "center"
    valign: "middle"

<ModernTextInput@TextInput>:
    size_hint_y: None
    height: dp(44)
    padding: dp(12), dp(11)
    font_size: "13sp"
    background_normal: ""
    background_active: ""
    background_color: .95, .96, .98, 1
    cursor_color: .10, .40, .80, 1
    hint_text_color: .55, .60, .68, 1
    foreground_color: .10, .14, .20, 1

<CardBox@BoxLayout>:
    padding: dp(12)
    spacing: dp(6)
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10)]

<TitleLabel@Label>:
    font_size: "18sp"
    bold: True
    color: .10, .14, .20, 1
    size_hint_y: None
    height: dp(36)
    halign: "left"
    valign: "middle"
    text_size: self.size

<SectionLabel@Label>:
    font_size: "13sp"
    bold: True
    color: .35, .40, .48, 1
    size_hint_y: None
    height: dp(28)
    halign: "left"
    valign: "middle"
    text_size: self.size

# --- Style Popup Serba Putih Global ---
<WhitePopup>:
    background_color: 1, 1, 1, 1
    background: ""
    title_color: 0.10, 0.14, 0.20, 1
    title_size: "16sp"
    separator_color: 0.85, 0.88, 0.92, 1

# --- Root Layout Utama ---
<RootLayout>:
    orientation: "vertical"
    canvas.before:
        Color:
            rgba: .94, .95, .97, 1
        Rectangle:
            pos: self.pos
            size: self.size

    # Clean Header Bar
    BoxLayout:
        size_hint_y: None
        height: dp(52)
        padding: dp(16), dp(8)
        canvas.before:
            Color:
                rgba: .08, .12, .18, 1
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: app.store_name
            font_size: "16sp"
            bold: True
            color: 1, 1, 1, 1
            halign: "left"
            valign: "middle"
            text_size: self.size

        Label:
            text: "v" + app.version
            size_hint_x: None
            width: dp(50)
            font_size: "11sp"
            color: .60, .68, .78, 1
            halign: "right"
            valign: "middle"
            text_size: self.size

    # Area Konten Utama
    ScreenManager:
        id: sm

        Screen:
            name: "dashboard"
            ScrollView:
                do_scroll_x: False
                BoxLayout:
                    orientation: "vertical"
                    padding: dp(16)
                    spacing: dp(12)
                    size_hint_y: None
                    height: self.minimum_height

                    TitleLabel:
                        text: "Ringkasan Hari Ini"

                    GridLayout:
                        cols: 2
                        spacing: dp(10)
                        size_hint_y: None
                        height: dp(160)

                        CardBox:
                            orientation: "vertical"
                            Label:
                                text: "PENJUALAN"
                                font_size: "10sp"
                                bold: True
                                color: .10, .50, .30, 1
                                halign: "left"
                                text_size: self.size
                            Label:
                                id: dash_sales
                                text: "Rp 0"
                                font_size: "16sp"
                                bold: True
                                color: .05, .35, .20, 1
                                halign: "left"
                                valign: "middle"
                                text_size: self.size

                        CardBox:
                            orientation: "vertical"
                            Label:
                                text: "TRANSAKSI"
                                font_size: "10sp"
                                bold: True
                                color: .15, .40, .70, 1
                                halign: "left"
                                text_size: self.size
                            Label:
                                id: dash_trx
                                text: "0"
                                font_size: "18sp"
                                bold: True
                                color: .10, .25, .50, 1
                                halign: "left"
                                valign: "middle"
                                text_size: self.size

                        CardBox:
                            orientation: "vertical"
                            Label:
                                text: "PRODUK AKTIF"
                                font_size: "10sp"
                                bold: True
                                color: .50, .25, .70, 1
                                halign: "left"
                                text_size: self.size
                            Label:
                                id: dash_products
                                text: "0"
                                font_size: "18sp"
                                bold: True
                                color: .35, .15, .50, 1
                                halign: "left"
                                valign: "middle"
                                text_size: self.size

                        CardBox:
                            orientation: "vertical"
                            Label:
                                text: "STOK MENIPIS"
                                font_size: "10sp"
                                bold: True
                                color: .80, .40, .10, 1
                                halign: "left"
                                text_size: self.size
                            Label:
                                id: dash_low
                                text: "0"
                                font_size: "18sp"
                                bold: True
                                color: .60, .25, .05, 1
                                halign: "left"
                                valign: "middle"
                                text_size: self.size

                    Button:
                        text: "Refresh Data"
                        size_hint_y: None
                        height: dp(42)
                        background_normal: ""
                        background_color: .12, .16, .22, 1
                        color: 1, 1, 1, 1
                        bold: True
                        on_release: app.refresh_all()

        Screen:
            name: "pos"
            BoxLayout:
                orientation: "vertical"
                padding: dp(12)
                spacing: dp(8)

                TitleLabel:
                    text: "Kasir / POS"

                ModernTextInput:
                    id: search_pos
                    hint_text: "Cari produk atau scan barcode..."
                    on_text: app.refresh_pos_products(self.text)

                ScrollView:
                    do_scroll_x: False
                    GridLayout:
                        id: product_grid
                        cols: 1
                        spacing: dp(6)
                        size_hint_y: None
                        height: self.minimum_height

                CardBox:
                    size_hint_y: None
                    height: dp(54)
                    padding: dp(8), dp(4)
                    spacing: dp(8)

                    BoxLayout:
                        orientation: "vertical"
                        Label:
                            id: cart_summary_items
                            text: "0 Item"
                            font_size: "11sp"
                            color: .40, .45, .55, 1
                            halign: "left"
                            text_size: self.size
                        Label:
                            id: pos_total
                            text: "Rp 0"
                            font_size: "15sp"
                            bold: True
                            color: .05, .55, .25, 1
                            halign: "left"
                            text_size: self.size

                    Button:
                        text: "Lihat Keranjang"
                        size_hint_x: None
                        width: dp(140)
                        background_normal: ""
                        background_color: .05, .60, .30, 1
                        color: 1, 1, 1, 1
                        bold: True
                        on_release: app.open_cart_popup()

        Screen:
            name: "products"
            BoxLayout:
                orientation: "vertical"
                padding: dp(12)
                spacing: dp(8)

                TitleLabel:
                    text: "Daftar Produk"

                BoxLayout:
                    size_hint_y: None
                    height: dp(44)
                    spacing: dp(6)

                    ModernTextInput:
                        id: search_product
                        hint_text: "Cari nama produk..."
                        on_text: app.refresh_products(self.text)

                    Button:
                        text: "+ Tambah"
                        size_hint_x: None
                        width: dp(95)
                        background_normal: ""
                        background_color: .04, .58, .30, 1
                        color: 1, 1, 1, 1
                        bold: True
                        on_release: app.product_form()

                Button:
                    text: "+ Tambah Kategori"
                    size_hint_y: None
                    height: dp(40)
                    background_normal: ""
                    background_color: .88, .91, .95, 1
                    color: .08, .11, .16, 1
                    bold: True
                    on_release: app.category_form()

                ScrollView:
                    do_scroll_x: False
                    GridLayout:
                        id: products_grid
                        cols: 1
                        spacing: dp(6)
                        size_hint_y: None
                        height: self.minimum_height

        Screen:
            name: "history"
            BoxLayout:
                orientation: "vertical"
                padding: dp(12)
                spacing: dp(8)

                TitleLabel:
                    text: "Riwayat Transaksi"

                ScrollView:
                    do_scroll_x: False
                    GridLayout:
                        id: history_grid
                        cols: 1
                        spacing: dp(6)
                        size_hint_y: None
                        height: self.minimum_height

        Screen:
            name: "reports"
            BoxLayout:
                orientation: "vertical"
                padding: dp(12)
                spacing: dp(8)

                TitleLabel:
                    text: "Laporan Penjualan"

                ScrollView:
                    do_scroll_x: False
                    GridLayout:
                        id: report_grid
                        cols: 1
                        spacing: dp(6)
                        size_hint_y: None
                        height: self.minimum_height

                Button:
                    text: "Export CSV"
                    size_hint_y: None
                    height: dp(44)
                    background_normal: ""
                    background_color: .04, .58, .30, 1
                    color: 1, 1, 1, 1
                    bold: True
                    on_release: app.export_csv()

        Screen:
            name: "settings"
            ScrollView:
                do_scroll_x: False
                BoxLayout:
                    orientation: "vertical"
                    padding: dp(12)
                    spacing: dp(8)
                    size_hint_y: None
                    height: self.minimum_height

                    TitleLabel:
                        text: "Pengaturan Toko"

                    SectionLabel:
                        text: "Identitas Toko"

                    ModernTextInput:
                        id: setting_store
                        hint_text: "Nama toko"
                        text: app.store_name

                    ModernTextInput:
                        id: setting_address
                        hint_text: "Alamat toko"
                        text: app.store_address

                    ModernTextInput:
                        id: setting_tax
                        hint_text: "Pajak (%)"
                        text: app.tax_percent
                        input_filter: "float"

                    ModernTextInput:
                        id: setting_cashier
                        hint_text: "Nama kasir"
                        text: app.cashier_name

                    Button:
                        text: "Simpan Pengaturan"
                        size_hint_y: None
                        height: dp(44)
                        background_normal: ""
                        background_color: .04, .58, .30, 1
                        color: 1, 1, 1, 1
                        bold: True
                        on_release: app.save_settings()

                    SectionLabel:
                        text: "Data & Backup"

                    Button:
                        text: "Buat Backup Database"
                        size_hint_y: None
                        height: dp(44)
                        background_normal: ""
                        background_color: .88, .91, .95, 1
                        color: .08, .11, .16, 1
                        bold: True
                        on_release: app.make_backup()

                    Label:
                        text: "Database SQLite lokal. Aplikasi tetap dapat digunakan tanpa internet."
                        text_size: self.width, None
                        halign: "left"
                        color: .30, .34, .40, 1
                        size_hint_y: None
                        height: dp(36)

    # Bottom Navigation Bar
    BoxLayout:
        size_hint_y: None
        height: dp(54)
        padding: dp(2)
        spacing: dp(2)
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
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
"""


class WhitePopup(Popup):
    pass


class RootLayout(BoxLayout):
    pass


class POSApp(App):
    version = __version__
    store_name = StringProperty("TOKO SAYA")
    store_address = StringProperty("")
    tax_percent = StringProperty("0")
    cashier_name = StringProperty("Admin")

    def build(self):
        self.title = "POS Kasir"
        self.db = Database(os.path.join(self.user_data_dir, "pos.db"))
        self.load_settings()
        self.cart = []
        self.cart_popup = None
        self.cart_popup_grid = None
        self.popup_total_label = None
        Builder.load_string(KV)
        return RootLayout()

    def on_start(self):
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
            self.update_cart_summary()
        elif name == "products":
            self.refresh_products("")
        elif name == "history":
            self.refresh_history()
        elif name == "reports":
            self.refresh_reports()

    def refresh_all(self):
        self.refresh_dashboard()
        self.refresh_pos_products("")
        self.update_cart_summary()
        self.refresh_products("")
        self.refresh_history()
        self.refresh_reports()

    @staticmethod
    def money(value):
        return "Rp {:,.0f}".format(float(value)).replace(",", ".")

    def refresh_dashboard(self):
        s, product_count, low = self.db.summary_today()
        self.root.ids.dash_sales.text = f"{self.money(s['total'])}"
        self.root.ids.dash_trx.text = f"{s['transactions']}"
        self.root.ids.dash_products.text = f"{product_count}"
        self.root.ids.dash_low.text = f"{low}"

    def refresh_pos_products(self, search):
        grid = self.root.ids.product_grid
        grid.clear_widgets()
        for p in self.db.products(search)[:100]:
            btn = Button(
                text=f"{p['name']}\n{self.money(p['sell_price'])}  •  Stok {p['stock']:g} {p['unit']}",
                size_hint_y=None, height=dp(56),
                background_normal="",
                background_color=(1, 1, 1, 1),
                color=(.08, .10, .14, 1),
                font_size="13sp",
                bold=True,
                halign="left",
                valign="middle",
                padding=(dp(12), dp(6))
            )
            btn.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0] - dp(24), None)))
            btn.bind(on_release=lambda b, pid=p["id"]: self.add_to_cart(pid))
            grid.add_widget(btn)

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
                self.update_cart_summary()
                return
        self.cart.append({
            "id": p["id"], "name": p["name"], "qty": 1,
            "price": float(p["sell_price"]), "discount": 0,
            "line_total": float(p["sell_price"])
        })
        self.update_cart_summary()

    def update_cart_summary(self):
        if not hasattr(self, "root") or not self.root:
            return
        subtotal, discount, tax, total, paid, change = self.recalculate_pos()
        total_items = sum(item["qty"] for item in self.cart)
        self.root.ids.cart_summary_items.text = f"{total_items:g} Item"
        self.root.ids.pos_total.text = self.money(total)

    def open_cart_popup(self):
        if not self.cart:
            self.info("Keranjang belanja masih kosong.")
            return

        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        
        scroll = ScrollView(do_scroll_x=False)
        self.cart_popup_grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        self.cart_popup_grid.bind(minimum_height=self.cart_popup_grid.setter('height'))
        
        scroll.add_widget(self.cart_popup_grid)
        content.add_widget(scroll)

        footer = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        self.popup_total_label = Label(
            text="Total: " + self.money(sum(x["line_total"] for x in self.cart)),
            bold=True, font_size="15sp", color=(0.05, 0.55, 0.25, 1),
            halign="left", valign="middle"
        )
        self.popup_total_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        
        btn_pay = Button(
            text="BAYAR", size_hint_x=None, width=dp(120),
            background_normal="", background_color=(0.05, 0.60, 0.30, 1),
            color=(1, 1, 1, 1), bold=True
        )
        btn_pay.bind(on_release=lambda instance: self.checkout())
        
        footer.add_widget(self.popup_total_label)
        footer.add_widget(btn_pay)
        content.add_widget(footer)

        self.cart_popup = WhitePopup(
            title="Keranjang Belanja",
            content=content,
            size_hint=(0.92, 0.75)
        )
        self.refresh_cart_popup_grid()
        self.cart_popup.open()

    def refresh_cart_popup_grid(self):
        if not self.cart_popup_grid:
            return
        
        self.cart_popup_grid.clear_widgets()
        for item in self.cart:
            row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))

            lbl = Label(
                text=f"{item['name']}\n{self.money(item['price'])} x {item['qty']:g} = {self.money(item['line_total'])}",
                halign="left", valign="middle", 
                color=(0.10, 0.14, 0.20, 1), # Hitam Pekat
                font_size="12sp", bold=True
            )
            lbl.bind(size=lambda instance, value: setattr(instance, 'text_size', value))

            minus = Button(text="-", size_hint_x=None, width=dp(36),
                           background_normal="", background_color=(0.90, 0.92, 0.95, 1),
                           color=(0.08, 0.10, 0.14, 1), font_size="14sp", bold=True)
            plus = Button(text="+", size_hint_x=None, width=dp(36),
                          background_normal="", background_color=(0.88, 0.95, 0.91, 1),
                          color=(0.04, 0.48, 0.25, 1), font_size="14sp", bold=True)
            delete = Button(text="x", size_hint_x=None, width=dp(36),
                            background_normal="", background_color=(0.98, 0.90, 0.90, 1),
                            color=(0.72, 0.12, 0.12, 1), font_size="12sp", bold=True)
            
            minus.bind(on_release=lambda btn, iid=item["id"]: self.change_qty(iid, -1))
            plus.bind(on_release=lambda btn, iid=item["id"]: self.change_qty(iid, 1))
            delete.bind(on_release=lambda btn, iid=item["id"]: self.remove_cart(iid))
            
            row.add_widget(lbl)
            row.add_widget(minus)
            row.add_widget(plus)
            row.add_widget(delete)
            self.cart_popup_grid.add_widget(row)

        subtotal, discount, tax, total, paid, change = self.recalculate_pos()
        if self.popup_total_label:
            self.popup_total_label.text = "Total: " + self.money(total)

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
        self.update_cart_summary()
        self.refresh_cart_popup_grid()

    def remove_cart(self, product_id):
        self.cart = [x for x in self.cart if x["id"] != product_id]
        self.update_cart_summary()
        if not self.cart and self.cart_popup:
            self.cart_popup.dismiss()
        else:
            self.refresh_cart_popup_grid()

    def recalculate_pos(self, *_):
        subtotal = sum(x["line_total"] for x in self.cart)
        discount = 0
        try:
            tax = max(0, float(self.tax_percent)) / 100 * max(0, subtotal - discount)
        except ValueError:
            tax = 0
        total = max(0, subtotal - discount + tax)
        paid = total
        change = 0
        return subtotal, discount, tax, total, paid, change

    def checkout(self):
        if not self.cart:
            self.info("Keranjang masih kosong.")
            return
        subtotal, discount, tax, total, paid, change = self.recalculate_pos()
        payment = "Tunai"
        invoice = self.db.save_sale(
            self.cart, subtotal, discount, tax, total, paid, change, payment
        )
        self.cart = []
        if self.cart_popup:
            self.cart_popup.dismiss()
        self.refresh_all()
        self.info(
            f"Transaksi Berhasil!\n\nNota: {invoice}\nTotal: {self.money(total)}"
        )

    def refresh_products(self, search):
        grid = self.root.ids.products_grid
        grid.clear_widgets()
        for p in self.db.products(search):
            row = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(4))
            row.add_widget(Label(
                text=f"{p['name']} | {p['barcode'] or '-'}\n"
                     f"Jual {self.money(p['sell_price'])} | Stok {p['stock']:g} {p['unit']}",
                halign="left",
                valign="middle",
                color=(.08,.10,.14,1),
                font_size="11sp"
            ))
            edit = Button(text="Edit", size_hint_x=None, width=dp(60),
                           background_normal="", background_color=(.88,.94,1,1),
                           color=(.10,.28,.55,1), bold=True)
            delete = Button(text="Hapus", size_hint_x=None, width=dp(60),
                            background_normal="", background_color=(.98,.90,.90,1),
                            color=(.72,.12,.12,1), bold=True)
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
        popup = WhitePopup(title="Produk", content=box, size_hint=(.9, .9))

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
        popup = WhitePopup(title="Kategori", content=box, size_hint=(.8, .35))

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
            row = BoxLayout(size_hint_y=None, height=dp(54))
            row.add_widget(Label(
                text=f"{s['invoice']} | {s['created_at'].replace('T',' ')}\n"
                     f"{s['payment_method']} | {self.money(s['total'])}",
                halign="left",
                valign="middle",
                color=(.08,.10,.14,1),
                font_size="11sp"
            ))
            b = Button(text="Detail", size_hint_x=None, width=dp(68),
                       background_normal="", background_color=(.88,.94,1,1),
                       color=(.10,.28,.55,1), bold=True)
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
            "---------------------------------------"
        ]
        for item in self.db.sale_items(sale_id):
            lines.append(
                f"{item['product_name']} x{item['qty']:g} = "
                f"{self.money(item['line_total'])}"
            )
        lines += [
            "---------------------------------------",
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
                size_hint_y=None, height=dp(40), color=(0.2, 0.2, 0.2, 1)
            ))
            return
        for r in rows:
            grid.add_widget(Label(
                text=f"{r['day']} | {r['transactions']} transaksi | "
                     f"Total {self.money(r['total'])}",
                size_hint_y=None, height=dp(40), halign="left", color=(0.1, 0.14, 0.2, 1)
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
        self.info("Pengaturan berhasil disimpan.")

    def make_backup(self):
        filename = f"backup_pos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        path = os.path.join(self.user_data_dir, filename)
        self.db.backup(path)
        self.info(f"Backup dibuat di:\n{path}")

    def info(self, message, title="Informasi"):
        content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        scroll = ScrollView(do_scroll_x=False)
        
        lbl = Label(
            text=message,
            font_size="13sp",
            color=(0.10, 0.14, 0.20, 1),
            size_hint_y=None,
            halign="left",
            valign="top"
        )
        lbl.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        lbl.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        
        scroll.add_widget(lbl)
        content.add_widget(scroll)

        popup = WhitePopup(
            title=title,
            content=content,
            size_hint=(0.85, 0.55)
        )
        popup.open()


if __name__ == "__main__":
    POSApp().run()
