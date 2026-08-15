import os
import sys
from datetime import datetime

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.utils import platform

from database import Database

# Manager Bluetooth Thermal Printer Native
class ThermalPrinterManager:
    @staticmethod
    def print_receipt(mac_address, text_content):
        if platform != 'android':
            return True, "Simulasi cetak (Desktop)"
        try:
            from jnius import autoclass
            BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
            UUID = autoclass('java.util.UUID')
            adapter = BluetoothAdapter.getDefaultAdapter()
            if not adapter or not adapter.isEnabled():
                return False, "Bluetooth tidak aktif"
            device = adapter.getRemoteDevice(mac_address)
            spp_uuid = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")
            socket = device.createRfcommSocketToServiceRecord(spp_uuid)
            socket.connect()
            stream = socket.getOutputStream()
            stream.write(bytes([0x1B, 0x40]))
            stream.write(text_content.encode('utf-8'))
            stream.write(bytes("\n\n\n", 'utf-8'))
            stream.write(bytes([0x1D, 0x56, 0x42, 0x00]))
            stream.flush()
            socket.close()
            return True, "Berhasil mencetak!"
        except Exception as e:
            return False, f"Gagal cetak: {str(e)}"

KV = """
#:import dp kivy.metrics.dp

BoxLayout:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: 0.95, 0.96, 0.98, 1
        Rectangle:
            pos: self.pos
            size: self.size

    # Header Bar
    BoxLayout:
        size_hint_y: None
        height: dp(56)
        padding: [dp(16), dp(8)]
        canvas.before:
            Color:
                rgba: 0.10, 0.14, 0.20, 1
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: app.store_name
            font_size: '18sp'
            bold: True
            color: 1, 1, 1, 1
            halign: 'left'
            valign: 'middle'
            text_size: self.size

        Label:
            text: "v" + app.version
            font_size: '12sp'
            color: 0.6, 0.7, 0.8, 1
            size_hint_x: None
            width: dp(50)
            valign: 'middle'

    # ScreenManager dengan 6 Tab (Dashboard, Kasir, Produk, Riwayat, Laporan, Pengaturan)
    ScreenManager:
        id: sm
        transition: FadeTransition(duration=0.15)

        # 1. Screen Dashboard
        Screen:
            name: 'dashboard'
            BoxLayout:
                orientation: 'vertical'
                padding: dp(16)
                spacing: dp(16)

                Label:
                    text: "Ringkasan Hari Ini"
                    font_size: '18sp'
                    bold: True
                    color: 0.1, 0.1, 0.1, 1
                    size_hint_y: None
                    height: dp(30)
                    halign: 'left'
                    text_size: self.size

                GridLayout:
                    cols: 2
                    spacing: dp(12)
                    size_hint_y: None
                    height: dp(120)

                    BoxLayout:
                        orientation: 'vertical'
                        padding: dp(12)
                        canvas.before:
                            Color:
                                rgba: 1, 1, 1, 1
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [dp(8),]
                        Label:
                            text: "PENJUALAN"
                            font_size: '11sp'
                            bold: True
                            color: 0.2, 0.6, 0.3, 1
                            halign: 'left'
                            text_size: self.size
                        Label:
                            id: dash_sales
                            text: "Rp 0"
                            font_size: '18sp'
                            bold: True
                            color: 0.1, 0.1, 0.1, 1
                            halign: 'left'
                            text_size: self.size

                    BoxLayout:
                        orientation: 'vertical'
                        padding: dp(12)
                        canvas.before:
                            Color:
                                rgba: 1, 1, 1, 1
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [dp(8),]
                        Label:
                            text: "TRANSAKSI"
                            font_size: '11sp'
                            bold: True
                            color: 0.12, 0.45, 0.88, 1
                            halign: 'left'
                            text_size: self.size
                        Label:
                            id: dash_tx
                            text: "0"
                            font_size: '18sp'
                            bold: True
                            color: 0.1, 0.1, 0.1, 1
                            halign: 'left'
                            text_size: self.size

                Widget: # Spacer

        # 2. Screen Kasir
        Screen:
            name: 'pos'
            BoxLayout:
                orientation: 'vertical'
                padding: dp(12)
                spacing: dp(10)

                TextInput:
                    id: pos_search
                    hint_text: "Cari produk..."
                    size_hint_y: None
                    height: dp(40)
                    multiline: False
                    on_text: app.refresh_pos_products(self.text)

                BoxLayout:
                    spacing: dp(10)
                    ScrollView:
                        size_hint_x: 0.55
                        GridLayout:
                            id: pos_product_grid
                            cols: 2
                            spacing: dp(6)
                            size_hint_y: None
                            height: self.minimum_height

                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_x: 0.45
                        padding: dp(8)
                        canvas.before:
                            Color:
                                rgba: 1, 1, 1, 1
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [dp(8),]

                        Label:
                            text: "Keranjang Belanja"
                            bold: True
                            color: 0.2, 0.2, 0.2, 1
                            size_hint_y: None
                            height: dp(24)

                        ScrollView:
                            BoxLayout:
                                id: cart_list
                                orientation: 'vertical'
                                size_hint_y: None
                                height: self.minimum_height
                                spacing: dp(4)

                        BoxLayout:
                            orientation: 'vertical'
                            size_hint_y: None
                            height: dp(80)
                            spacing: dp(4)

                            Label:
                                text: "Total: " + app.money(app.cart_total)
                                bold: True
                                font_size: '15sp'
                                color: 0.12, 0.45, 0.88, 1

                            Button:
                                text: "BAYAR"
                                background_normal: ''
                                background_color: 0.12, 0.45, 0.88, 1
                                bold: True
                                on_release: app.open_checkout_popup()

        # 3. Screen Produk
        Screen:
            name: 'products'
            BoxLayout:
                orientation: 'vertical'
                padding: dp(12)
                spacing: dp(8)

                BoxLayout:
                    size_hint_y: None
                    height: dp(40)
                    spacing: dp(8)

                    TextInput:
                        hint_text: "Cari produk..."
                        multiline: False
                        on_text: app.refresh_product_list(self.text)

                    Button:
                        text: "+ Tambah"
                        size_hint_x: None
                        width: dp(90)
                        background_normal: ''
                        background_color: 0.12, 0.45, 0.88, 1
                        on_release: app.open_product_modal()

                ScrollView:
                    BoxLayout:
                        id: product_crud_list
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(4)

        # 4. Screen Riwayat
        Screen:
            name: 'history'
            BoxLayout:
                orientation: 'vertical'
                padding: dp(12)
                ScrollView:
                    BoxLayout:
                        id: history_list
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(4)

        # 5. Screen Laporan
        Screen:
            name: 'reports'
            BoxLayout:
                orientation: 'vertical'
                padding: dp(16)
                spacing: dp(12)

                Label:
                    text: "Laporan Ringkas"
                    font_size: '16sp'
                    bold: True
                    color: 0.1, 0.1, 0.1, 1
                    size_hint_y: None
                    height: dp(30)

                Label:
                    id: report_total_sales
                    text: "Total Omset: Rp 0"
                    color: 0.2, 0.2, 0.2, 1
                    size_hint_y: None
                    height: dp(24)

                Widget:

        # 6. Screen Pengaturan
        Screen:
            name: 'settings'
            ScrollView:
                BoxLayout:
                    orientation: 'vertical'
                    padding: dp(16)
                    spacing: dp(10)
                    size_hint_y: None
                    height: self.minimum_height

                    Label:
                        text: "Pengaturan Toko & Printer"
                        bold: True
                        color: 0.12, 0.45, 0.88, 1
                        size_hint_y: None
                        height: dp(24)

                    TextInput:
                        id: set_store
                        hint_text: "Nama Toko"
                        text: app.store_name
                        size_hint_y: None
                        height: dp(40)

                    TextInput:
                        id: set_address
                        hint_text: "Alamat Toko"
                        text: app.store_address
                        size_hint_y: None
                        height: dp(40)

                    TextInput:
                        id: set_bt
                        hint_text: "MAC Address Bluetooth Thermal Printer"
                        text: app.bt_mac_address
                        size_hint_y: None
                        height: dp(40)

                    Button:
                        text: "SIMPAN PENGATURAN"
                        size_hint_y: None
                        height: dp(44)
                        background_normal: ''
                        background_color: 0.12, 0.45, 0.88, 1
                        bold: True
                        on_release: app.save_settings()

    # Bottom Navigation Bar (6 Tab Sesuai Foto)
    BoxLayout:
        size_hint_y: None
        height: dp(54)
        padding: [dp(2), dp(2)]
        spacing: dp(2)
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size

        Button:
            text: "Dashboard"
            font_size: '10sp'
            background_normal: ''
            background_color: (0.12, 0.45, 0.88, 1) if sm.current == 'dashboard' else (0.9, 0.9, 0.9, 1)
            color: (1, 1, 1, 1) if sm.current == 'dashboard' else (0.3, 0.3, 0.3, 1)
            on_release: sm.current = 'dashboard'

        Button:
            text: "Kasir"
            font_size: '10sp'
            background_normal: ''
            background_color: (0.12, 0.45, 0.88, 1) if sm.current == 'pos' else (0.9, 0.9, 0.9, 1)
            color: (1, 1, 1, 1) if sm.current == 'pos' else (0.3, 0.3, 0.3, 1)
            on_release: sm.current = 'pos'

        Button:
            text: "Produk"
            font_size: '10sp'
            background_normal: ''
            background_color: (0.12, 0.45, 0.88, 1) if sm.current == 'products' else (0.9, 0.9, 0.9, 1)
            color: (1, 1, 1, 1) if sm.current == 'products' else (0.3, 0.3, 0.3, 1)
            on_release: sm.current = 'products'

        Button:
            text: "Riwayat"
            font_size: '10sp'
            background_normal: ''
            background_color: (0.12, 0.45, 0.88, 1) if sm.current == 'history' else (0.9, 0.9, 0.9, 1)
            color: (1, 1, 1, 1) if sm.current == 'history' else (0.3, 0.3, 0.3, 1)
            on_release: sm.current = 'history'

        Button:
            text: "Laporan"
            font_size: '10sp'
            background_normal: ''
            background_color: (0.12, 0.45, 0.88, 1) if sm.current == 'reports' else (0.9, 0.9, 0.9, 1)
            color: (1, 1, 1, 1) if sm.current == 'reports' else (0.3, 0.3, 0.3, 1)
            on_release: sm.current = 'reports'

        Button:
            text: "Pengaturan"
            font_size: '10sp'
            background_normal: ''
            background_color: (0.12, 0.45, 0.88, 1) if sm.current == 'settings' else (0.9, 0.9, 0.9, 1)
            color: (1, 1, 1, 1) if sm.current == 'settings' else (0.3, 0.3, 0.3, 1)
            on_release: sm.current = 'settings'
"""

class POSApp(App):
    version = "1.0.0"
    store_name = StringProperty("TOKO SAYA")
    store_address = StringProperty("")
    bt_mac_address = StringProperty("")
    cart = ListProperty([])
    cart_total = NumericProperty(0)

    def build(self):
        # Inisialisasi Database dengan Aman
        try:
            self.db = Database()
        except Exception:
            self.db = None
            
        return Builder.load_string(KV)

    def on_start(self):
        # PERBAIKAN PENTING: Diberikan SILENCE GUARD (Aplikasi TETAP BERJALAN walau data gagal dibaca)
        try:
            self.load_settings()
            self.refresh_all()
        except Exception as e:
            print(f"Abaikan Error Startup: {e}")

    def money(self, val):
        try:
            return f"Rp {float(val):,.0f}".replace(",", ".")
        except:
            return "Rp 0"

    def load_settings(self):
        if not self.db: return
        self.store_name = self.db.get_setting("store_name", "TOKO SAYA")
        self.store_address = self.db.get_setting("store_address", "")
        self.bt_mac_address = self.db.get_setting("bt_mac_address", "")

    def save_settings(self):
        if not self.db: return
        ids = self.root.ids
        self.db.set_setting("store_name", ids.set_store.text.strip() or "TOKO SAYA")
        self.db.set_setting("store_address", ids.set_address.text.strip())
        self.db.set_setting("bt_mac_address", ids.set_bt.text.strip())
        self.load_settings()
        self.info("Pengaturan Disimpan")

    def refresh_all(self):
        if not self.db: return
        self.refresh_dashboard()
        self.refresh_pos_products()
        self.refresh_product_list()
        self.refresh_history_list()

    def refresh_dashboard(self):
        try:
            summary = self.db.get_today_summary()
            self.root.ids.dash_sales.text = self.money(summary.get('total_sales', 0))
            self.root.ids.dash_tx.text = str(summary.get('total_transactions', 0))
        except Exception:
            pass

    def refresh_pos_products(self, query=""):
        if not self.db: return
        grid = self.root.ids.pos_product_grid
        grid.clear_widgets()
        for p in self.db.get_products(query):
            btn = Button(
                text=f"{p['name']}\n{self.money(p['price'])}\nStok: {p['stock']}",
                size_hint_y=None, height=dp(64),
                background_normal='', background_color=(1,1,1,1),
                color=(0.1,0.1,0.1,1), font_size='11sp'
            )
            btn.bind(on_release=lambda x, prod=p: self.add_to_cart(prod))
            grid.add_widget(btn)

    def add_to_cart(self, product):
        for item in self.cart:
            if item['id'] == product['id']:
                if item['qty'] + 1 > product['stock']: return
                item['qty'] += 1
                item['line_total'] = item['qty'] * item['price']
                self.update_cart_ui()
                return
        if product['stock'] < 1: return
        self.cart.append({'id': product['id'], 'name': product['name'], 'price': product['price'], 'qty': 1, 'stock': product['stock'], 'line_total': product['price']})
        self.update_cart_ui()

    def update_cart_ui(self):
        container = self.root.ids.cart_list
        container.clear_widgets()
        total = 0
        for item in self.cart:
            total += item['line_total']
            row = BoxLayout(size_hint_y=None, height=dp(30))
            row.add_widget(Label(text=item['name'], font_size='10sp', color=(0.1,0.1,0.1,1)))
            row.add_widget(Label(text=f"x{item['qty']}", font_size='10sp', color=(0.3,0.3,0.3,1)))
            row.add_widget(Label(text=self.money(item['line_total']), font_size='10sp', color=(0.1,0.1,0.1,1)))
            container.add_widget(row)
        self.cart_total = total

    def open_checkout_popup(self):
        if not self.cart: return
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
        content.add_widget(Label(text=f"Total: {self.money(self.cart_total)}", bold=True))
        pay_input = TextInput(hint_text="Jumlah Bayar", input_filter='int', multiline=False, size_hint_y=None, height=dp(40))
        content.add_widget(pay_input)
        
        popup = Popup(title="Bayar", content=content, size_hint=(0.8, 0.4))
        btn = Button(text="PROSES & CETAK", size_hint_y=None, height=dp(40), background_normal='', background_color=(0.12,0.45,0.88,1))
        
        def process(x):
            try: paid = float(pay_input.text)
            except: return
            if paid < self.cart_total: return
            change = paid - self.cart_total
            inv = f"INV{datetime.now().strftime('%Y%m%d%H%M%S')}"
            self.db.add_sale(inv, self.cart, self.cart_total, paid, change)
            popup.dismiss()
            if self.bt_mac_address.strip():
                ThermalPrinterManager.print_receipt(self.bt_mac_address.strip(), f"FAKTUR: {inv}\nTOTAL: {self.cart_total}\nBAYAR: {paid}\nKEMBALI: {change}")
            self.cart = []
            self.update_cart_ui()
            self.refresh_all()
            self.info(f"Kembali: {self.money(change)}")

        btn.bind(on_release=process)
        content.add_widget(btn)
        popup.open()

    def refresh_product_list(self, query=""):
        if not self.db: return
        container = self.root.ids.product_crud_list
        container.clear_widgets()
        for p in self.db.get_products(query):
            row = BoxLayout(size_hint_y=None, height=dp(36))
            row.add_widget(Label(text=p['name'], font_size='11sp', color=(0.1,0.1,0.1,1)))
            row.add_widget(Label(text=self.money(p['price']), font_size='11sp', color=(0.1,0.1,0.1,1)))
            container.add_widget(row)

    def open_product_modal(self):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(6))
        txt_n = TextInput(hint_text="Nama", multiline=False)
        txt_p = TextInput(hint_text="Harga", input_filter='int', multiline=False)
        txt_s = TextInput(hint_text="Stok", input_filter='int', multiline=False)
        content.add_widget(txt_n); content.add_widget(txt_p); content.add_widget(txt_s)
        popup = Popup(title="Tambah Produk", content=content, size_hint=(0.8, 0.45))
        btn = Button(text="SIMPAN", size_hint_y=None, height=dp(36), background_normal='', background_color=(0.12,0.45,0.88,1))
        def save(x):
            try: self.db.add_product(txt_n.text.strip(), float(txt_p.text), int(txt_s.text))
            except: pass
            popup.dismiss()
            self.refresh_all()
        btn.bind(on_release=save)
        content.add_widget(btn)
        popup.open()

    def refresh_history_list(self):
        if not self.db: return
        container = self.root.ids.history_list
        container.clear_widgets()
        sales = self.db.get_sales()
        total_omset = sum(s['total_amount'] for s in sales)
        self.root.ids.report_total_sales.text = f"Total Omset: {self.money(total_omset)}"
        for s in sales:
            row = BoxLayout(size_hint_y=None, height=dp(36))
            row.add_widget(Label(text=s['invoice_no'], font_size='10sp', color=(0.1,0.1,0.1,1)))
            row.add_widget(Label(text=self.money(s['total_amount']), font_size='10sp', color=(0.12,0.45,0.88,1)))
            container.add_widget(row)

    def info(self, msg):
        Popup(title="Info", content=Label(text=msg), size_hint=(0.7, 0.25)).open()

if __name__ == '__main__':
    POSApp().run()
