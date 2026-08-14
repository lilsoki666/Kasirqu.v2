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

# --- ESC/POS PRINTING DIRECT VIA ANDROID BLUETOOTH ---
class ThermalPrinterManager:
    @staticmethod
    def print_receipt(mac_address, text_content):
        if platform != 'android':
            print("--- SIMULASI CETAK PRINTER (Bukan Android) ---")
            print(text_content)
            print("---------------------------------------------")
            return True, "Simulasi cetak sukses (Desktop mode)"
        
        try:
            from jnius import autoclass
            BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
            UUID = autoclass('java.util.UUID')
            
            adapter = BluetoothAdapter.getDefaultAdapter()
            if not adapter or not adapter.isEnabled():
                return False, "Bluetooth tidak aktif/tersedia"
            
            device = adapter.getRemoteDevice(mac_address)
            spp_uuid = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")
            
            socket = device.createRfcommSocketToServiceRecord(spp_uuid)
            socket.connect()
            
            output_stream = socket.getOutputStream()
            
            INIT_PRINTER = bytes([0x1B, 0x40])
            FEED_PAPER   = bytes([0x1D, 0x56, 0x42, 0x00])
            
            output_stream.write(INIT_PRINTER)
            output_stream.write(text_content.encode('utf-8'))
            output_stream.write(bytes("\n\n\n", 'utf-8'))
            output_stream.write(FEED_PAPER)
            
            output_stream.flush()
            socket.close()
            return True, "Struk berhasil dicetak!"
        except Exception as e:
            return False, f"Gagal mencetak: {str(e)}"


KV = """
#:import dp kivy.metrics.dp

<ModernTextInput@TextInput>:
    padding: [dp(12), dp(10), dp(12), dp(10)]
    background_normal: ''
    background_active: ''
    background_color: 0.95, 0.96, 0.98, 1
    cursor_color: 0.1, 0.1, 0.1, 1
    foreground_color: 0.1, 0.1, 0.1, 1
    font_size: '14sp'

<PrimaryButton@Button>:
    background_normal: ''
    background_color: 0.12, 0.45, 0.88, 1
    color: 1, 1, 1, 1
    font_size: '14sp'
    bold: True

<DangerButton@Button>:
    background_normal: ''
    background_color: 0.88, 0.22, 0.22, 1
    color: 1, 1, 1, 1
    font_size: '14sp'
    bold: True

<SectionLabel@Label>:
    font_size: '16sp'
    bold: True
    color: 0.12, 0.45, 0.88, 1
    size_hint_y: None
    height: dp(30)
    halign: 'left'
    valign: 'middle'
    text_size: self.size

BoxLayout:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: 0.96, 0.97, 0.99, 1
        Rectangle:
            pos: self.pos
            size: self.size

    # Header Bar
    BoxLayout:
        size_hint_y: None
        height: dp(56)
        padding: [dp(16), dp(8)]
        spacing: dp(12)
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

    # Main Area / ScreenManager
    ScreenManager:
        id: sm
        transition: FadeTransition(duration=0.15)

        # Screen 1: Transaksi
        Screen:
            name: 'pos'
            BoxLayout:
                orientation: 'vertical'
                padding: dp(12)
                spacing: dp(10)

                BoxLayout:
                    size_hint_y: None
                    height: dp(42)
                    spacing: dp(8)

                    ModernTextInput:
                        id: pos_search
                        hint_text: "Cari produk atau scan barcode..."
                        on_text: app.filter_pos_products(self.text)

                BoxLayout:
                    spacing: dp(10)

                    ScrollView:
                        size_hint_x: 0.55
                        GridLayout:
                            id: pos_product_grid
                            cols: 2
                            spacing: dp(8)
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
                            font_size: '14sp'
                            bold: True
                            color: 0.2, 0.2, 0.2, 1
                            size_hint_y: None
                            height: dp(28)

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
                            height: dp(110)
                            padding: [0, dp(8), 0, 0]
                            spacing: dp(4)

                            BoxLayout:
                                Label:
                                    text: "Total:"
                                    color: 0.3, 0.3, 0.3, 1
                                    halign: 'left'
                                    text_size: self.size
                                Label:
                                    text: app.money(app.cart_total)
                                    bold: True
                                    font_size: '16sp'
                                    color: 0.12, 0.45, 0.88, 1
                                    halign: 'right'
                                    text_size: self.size

                            PrimaryButton:
                                text: "BAYAR"
                                size_hint_y: None
                                height: dp(44)
                                on_release: app.open_checkout_popup()

        # Screen 2: Kelola Produk
        Screen:
            name: 'products'
            BoxLayout:
                orientation: 'vertical'
                padding: dp(12)
                spacing: dp(10)

                BoxLayout:
                    size_hint_y: None
                    height: dp(42)
                    spacing: dp(8)

                    ModernTextInput:
                        id: prod_search
                        hint_text: "Cari produk..."
                        on_text: app.refresh_product_list(self.text)

                    PrimaryButton:
                        text: "+ Tambah"
                        size_hint_x: None
                        width: dp(100)
                        on_release: app.open_product_modal()

                ScrollView:
                    BoxLayout:
                        id: product_crud_list
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(6)

        # Screen 3: Riwayat Transaksi
        Screen:
            name: 'history'
            BoxLayout:
                orientation: 'vertical'
                padding: dp(12)
                spacing: dp(10)

                BoxLayout:
                    size_hint_y: None
                    height: dp(36)
                    SectionLabel:
                        text: "Riwayat Penjualan"
                        size_hint_x: 0.5
                    Label:
                        id: history_total_label
                        text: "Total Omset: Rp 0"
                        bold: True
                        font_size: '13sp'
                        color: 0.12, 0.45, 0.88, 1
                        halign: 'right'
                        valign: 'middle'
                        text_size: self.size
                        size_hint_x: 0.5

                ScrollView:
                    BoxLayout:
                        id: history_list
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(6)

        # Screen 4: Pengaturan Toko
        Screen:
            name: 'settings'
            ScrollView:
                BoxLayout:
                    orientation: 'vertical'
                    padding: dp(16)
                    spacing: dp(12)
                    size_hint_y: None
                    height: self.minimum_height

                    SectionLabel:
                        text: "Informasi Toko"

                    ModernTextInput:
                        id: setting_store
                        hint_text: "Nama Toko"
                        text: app.store_name

                    ModernTextInput:
                        id: setting_address
                        hint_text: "Alamat Toko"
                        text: app.store_address

                    ModernTextInput:
                        id: setting_cashier
                        hint_text: "Nama Kasir Default"
                        text: app.cashier_name

                    SectionLabel:
                        text: "Printer Thermal Bluetooth"

                    ModernTextInput:
                        id: setting_bt_mac
                        hint_text: "MAC Address Printer Bluetooth"
                        text: app.bt_mac_address

                    PrimaryButton:
                        text: "SIMPAN PENGATURAN"
                        size_hint_y: None
                        height: dp(44)
                        on_release: app.save_settings()

    # Navigation Bar
    BoxLayout:
        size_hint_y: None
        height: dp(54)
        padding: [dp(4), dp(4)]
        spacing: dp(4)
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size

        Button:
            text: "Kasir"
            background_normal: ''
            background_color: (0.12, 0.45, 0.88, 1) if sm.current == 'pos' else (0.9, 0.9, 0.9, 1)
            color: (1, 1, 1, 1) if sm.current == 'pos' else (0.3, 0.3, 0.3, 1)
            bold: True
            on_release: sm.current = 'pos'

        Button:
            text: "Produk"
            background_normal: ''
            background_color: (0.12, 0.45, 0.88, 1) if sm.current == 'products' else (0.9, 0.9, 0.9, 1)
            color: (1, 1, 1, 1) if sm.current == 'products' else (0.3, 0.3, 0.3, 1)
            bold: True
            on_release: sm.current = 'products'

        Button:
            text: "Riwayat"
            background_normal: ''
            background_color: (0.12, 0.45, 0.88, 1) if sm.current == 'history' else (0.9, 0.9, 0.9, 1)
            color: (1, 1, 1, 1) if sm.current == 'history' else (0.3, 0.3, 0.3, 1)
            bold: True
            on_release: sm.current = 'history'

        Button:
            text: "Pengaturan"
            background_normal: ''
            background_color: (0.12, 0.45, 0.88, 1) if sm.current == 'settings' else (0.9, 0.9, 0.9, 1)
            color: (1, 1, 1, 1) if sm.current == 'settings' else (0.3, 0.3, 0.3, 1)
            bold: True
            on_release: sm.current = 'settings'
"""

class POSApp(App):
    version = "2.1.0"
    store_name = StringProperty("TOKO SAYA")
    store_address = StringProperty("")
    tax_percent = StringProperty("0")
    cashier_name = StringProperty("Admin")
    bt_mac_address = StringProperty("")

    cart = ListProperty([])
    cart_total = NumericProperty(0)

    def build(self):
        self.db = Database()
        self.load_settings()
        return Builder.load_string(KV)

    def on_start(self):
        self.refresh_all()
        # Request Izin Bluetooth Android otomatis agar tidak crash
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.BLUETOOTH_CONNECT,
                    Permission.BLUETOOTH_SCAN,
                    Permission.BLUETOOTH_ADMIN
                ])
            except Exception as e:
                print("Permission request bypass:", e)

    def money(self, val):
        try:
            return f"Rp {float(val):,.0f}".replace(",", ".")
        except:
            return "Rp 0"

    def load_settings(self):
        self.store_name = self.db.get_setting("store_name", "TOKO SAYA")
        self.store_address = self.db.get_setting("store_address", "")
        self.tax_percent = self.db.get_setting("tax_percent", "0")
        self.cashier_name = self.db.get_setting("cashier_name", "Admin")
        self.bt_mac_address = self.db.get_setting("bt_mac_address", "")

    def save_settings(self):
        ids = self.root.ids
        self.db.set_setting("store_name", ids.setting_store.text.strip() or "TOKO SAYA")
        self.db.set_setting("store_address", ids.setting_address.text.strip())
        self.db.set_setting("cashier_name", ids.setting_cashier.text.strip() or "Admin")
        self.db.set_setting("bt_mac_address", ids.setting_bt_mac.text.strip())
        
        self.load_settings()
        self.refresh_all()
        self.info("Pengaturan berhasil disimpan.")

    def refresh_all(self):
        self.refresh_pos_products()
        self.refresh_product_list()
        self.refresh_history_list()

    def refresh_pos_products(self, query=""):
        grid = self.root.ids.pos_product_grid
        grid.clear_widgets()
        products = self.db.get_products(query)
        for p in products:
            btn = Button(
                text=f"{p['name']}\n{self.money(p['price'])}\nStok: {p['stock']}",
                size_hint_y=None,
                height=dp(70),
                background_normal='',
                background_color=(1, 1, 1, 1),
                color=(0.1, 0.1, 0.1, 1),
                font_size='12sp'
            )
            btn.bind(on_release=lambda x, prod=p: self.add_to_cart(prod))
            grid.add_widget(btn)

    def filter_pos_products(self, text):
        self.refresh_pos_products(text)

    def add_to_cart(self, product):
        for item in self.cart:
            if item['id'] == product['id']:
                if item['qty'] + 1 > product['stock']:
                    self.info("Stok tidak mencukupi!")
                    return
                item['qty'] += 1
                item['line_total'] = item['qty'] * item['price']
                self.update_cart_ui()
                return

        if product['stock'] < 1:
            self.info("Stok habis!")
            return

        self.cart.append({
            'id': product['id'],
            'name': product['name'],
            'price': product['price'],
            'qty': 1,
            'stock': product['stock'],
            'line_total': product['price']
        })
        self.update_cart_ui()

    def update_cart_ui(self):
        container = self.root.ids.cart_list
        container.clear_widgets()
        total = 0

        for idx, item in enumerate(self.cart):
            total += item['line_total']
            row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(2))
            row.add_widget(Label(text=item['name'], font_size='10sp', color=(0.1, 0.1, 0.1, 1), size_hint_x=0.35))
            
            # Tombol - & + Kuantitas
            btn_minus = Button(text="-", size_hint_x=0.1, background_normal='', background_color=(0.8, 0.8, 0.8, 1), color=(0,0,0,1))
            btn_minus.bind(on_release=lambda x, i=idx: self.change_cart_qty(i, -1))
            row.add_widget(btn_minus)

            row.add_widget(Label(text=f"{item['qty']}", font_size='11sp', color=(0.3, 0.3, 0.3, 1), size_hint_x=0.1))

            btn_plus = Button(text="+", size_hint_x=0.1, background_normal='', background_color=(0.8, 0.8, 0.8, 1), color=(0,0,0,1))
            btn_plus.bind(on_release=lambda x, i=idx: self.change_cart_qty(i, 1))
            row.add_widget(btn_plus)

            row.add_widget(Label(text=self.money(item['line_total']), font_size='10sp', color=(0.1, 0.1, 0.1, 1), size_hint_x=0.25))
            
            del_btn = Button(text="X", size_hint_x=0.1, background_normal='', background_color=(0.9, 0.3, 0.3, 1), color=(1,1,1,1))
            del_btn.bind(on_release=lambda x, i=idx: self.remove_cart_item(i))
            row.add_widget(del_btn)
            
            container.add_widget(row)

        self.cart_total = total

    def change_cart_qty(self, index, delta):
        if 0 <= index < len(self.cart):
            item = self.cart[index]
            new_qty = item['qty'] + delta
            if new_qty <= 0:
                self.remove_cart_item(index)
            elif new_qty > item['stock']:
                self.info("Stok produk tidak mencukupi!")
            else:
                item['qty'] = new_qty
                item['line_total'] = item['qty'] * item['price']
                self.update_cart_ui()

    def remove_cart_item(self, index):
        if 0 <= index < len(self.cart):
            self.cart.pop(index)
            self.update_cart_ui()

    def open_checkout_popup(self):
        if not self.cart:
            self.info("Keranjang masih kosong!")
            return

        content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        content.add_widget(Label(text=f"Total: {self.money(self.cart_total)}", font_size='16sp', bold=True))
        
        pay_input = TextInput(hint_text="Jumlah Uang Bayar", input_filter='int', multiline=False, size_hint_y=None, height=dp(40))
        content.add_widget(pay_input)

        # Tombol Quick Money (Uang Pas, 10k, 20k, 50k, 100k)
        qm_box = BoxLayout(spacing=dp(4), size_hint_y=None, height=dp(32))
        quick_amounts = [("Pas", self.cart_total), ("10k", 10000), ("20k", 20000), ("50k", 50000), ("100k", 100000)]
        for label_text, val in quick_amounts:
            btn_qm = Button(text=label_text, font_size='11sp', background_normal='', background_color=(0.85, 0.88, 0.92, 1), color=(0.1, 0.1, 0.1, 1))
            btn_qm.bind(on_release=lambda x, v=val: setattr(pay_input, 'text', str(int(v))))
            qm_box.add_widget(btn_qm)
        content.add_widget(qm_box)

        popup = Popup(title="Pembayaran", content=content, size_hint=(0.85, 0.55))

        btn_box = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(40))
        btn_confirm = Button(text="PROSES & CETAK", background_normal='', background_color=(0.12, 0.45, 0.88, 1))
        btn_confirm.bind(on_release=lambda x: self.process_checkout(pay_input.text, popup))
        btn_box.add_widget(btn_confirm)
        
        content.add_widget(btn_box)
        popup.open()

    def process_checkout(self, paid_amount_str, popup):
        try:
            paid = float(paid_amount_str)
        except:
            self.info("Nominal pembayaran tidak valid!")
            return

        if paid < self.cart_total:
            self.info("Uang pembayaran kurang!")
            return

        change = paid - self.cart_total
        invoice = f"INV{datetime.now().strftime('%Y%m%d%H%M%S')}"

        success, msg = self.db.add_sale(invoice, self.cart, self.cart_total, paid, change)
        if not success:
            self.info(f"Gagal simpan: {msg}")
            return

        popup.dismiss()

        receipt_text = self.generate_receipt_text(invoice, self.cart, self.cart_total, paid, change)

        if self.bt_mac_address.strip():
            printed, p_msg = ThermalPrinterManager.print_receipt(self.bt_mac_address.strip(), receipt_text)
            self.info(f"Transaksi Sukses! Kembali: {self.money(change)}\n({p_msg})")
        else:
            self.info(f"Transaksi Sukses! Kembali: {self.money(change)}\n(Printer tidak dikonfigurasi)")

        self.cart = []
        self.update_cart_ui()
        self.refresh_all()

    def generate_receipt_text(self, invoice, cart_items, total, paid, change, date_str=None):
        lines = []
        LINE_WIDTH = 32
        
        lines.append(self.store_name.center(LINE_WIDTH))
        if self.store_address:
            lines.append(self.store_address.center(LINE_WIDTH))
            
        lines.append("-" * LINE_WIDTH)
        lines.append(f"No  : {invoice}")
        tgl = date_str if date_str else datetime.now().strftime('%Y-%m-%d %H:%M')
        lines.append(f"Tgl : {tgl}")
        lines.append(f"Ksr : {self.cashier_name}")
        lines.append("-" * LINE_WIDTH)
        
        for item in cart_items:
            lines.append(f"{item['name']}")
            qty_price = f"  {item['qty']:g} x {item['price']:,.0f}".replace(",", ".")
            item_total = f"{item['line_total']:,.0f}".replace(",", ".")
            spaces = LINE_WIDTH - len(qty_price) - len(item_total)
            lines.append(qty_price + (" " * max(1, spaces)) + item_total)
            
        lines.append("-" * LINE_WIDTH)
        
        tot_str = self.money(total)
        paid_str = self.money(paid)
        change_str = self.money(change)
        
        lines.append("Total  :".ljust(12) + tot_str.rjust(20))
        lines.append("Bayar  :".ljust(12) + paid_str.rjust(20))
        lines.append("Kembali:".ljust(12) + change_str.rjust(20))
        
        lines.append("-" * LINE_WIDTH)
        lines.append("Terima Kasih Atas Kunjungan Anda!".center(LINE_WIDTH))
        
        return "\n".join(lines)

    def refresh_product_list(self, query=""):
        container = self.root.ids.product_crud_list
        container.clear_widgets()
        products = self.db.get_products(query)
        for p in products:
            row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(4))
            row.add_widget(Label(text=p['name'], font_size='12sp', color=(0.1, 0.1, 0.1, 1), size_hint_x=0.35))
            row.add_widget(Label(text=self.money(p['price']), font_size='12sp', color=(0.1, 0.1, 0.1, 1), size_hint_x=0.25))
            row.add_widget(Label(text=f"Stok: {p['stock']}", font_size='12sp', color=(0.3, 0.3, 0.3, 1), size_hint_x=0.15))
            
            btn_edit = Button(text="Edit", size_hint_x=0.12, background_normal='', background_color=(0.12, 0.45, 0.88, 1))
            btn_edit.bind(on_release=lambda x, prod=p: self.open_product_modal(prod))
            row.add_widget(btn_edit)

            btn_del = Button(text="Hapus", size_hint_x=0.13, background_normal='', background_color=(0.88, 0.22, 0.22, 1))
            btn_del.bind(on_release=lambda x, prod=p: self.confirm_delete_product(prod))
            row.add_widget(btn_del)
            
            container.add_widget(row)

    def confirm_delete_product(self, product):
        content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        content.add_widget(Label(text=f"Hapus produk '{product['name']}'?", halign='center'))
        
        popup = Popup(title="Konfirmasi Hapus", content=content, size_hint=(0.75, 0.3))
        
        btn_box = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(36))
        btn_yes = Button(text="Ya, Hapus", background_normal='', background_color=(0.88, 0.22, 0.22, 1))
        btn_yes.bind(on_release=lambda x: [self.db.delete_product(product['id']), popup.dismiss(), self.refresh_all()])
        
        btn_no = Button(text="Batal", background_normal='', background_color=(0.6, 0.6, 0.6, 1))
        btn_no.bind(on_release=popup.dismiss)
        
        btn_box.add_widget(btn_yes)
        btn_box.add_widget(btn_no)
        content.add_widget(btn_box)
        popup.open()

    def open_product_modal(self, product=None):
        content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        
        txt_name = TextInput(hint_text="Nama Produk", text=product['name'] if product else "", multiline=False)
        txt_price = TextInput(hint_text="Harga", text=str(int(product['price'])) if product else "", input_filter='int', multiline=False)
        txt_stock = TextInput(hint_text="Stok", text=str(int(product['stock'])) if product else "", input_filter='int', multiline=False)
        
        content.add_widget(txt_name)
        content.add_widget(txt_price)
        content.add_widget(txt_stock)

        popup = Popup(title="Form Produk" if not product else "Edit Produk", content=content, size_hint=(0.85, 0.5))

        btn_save = Button(text="SIMPAN", size_hint_y=None, height=dp(40), background_normal='', background_color=(0.12, 0.45, 0.88, 1))
        
        def save(x):
            name = txt_name.text.strip()
            try:
                price = float(txt_price.text)
                stock = int(txt_stock.text)
            except:
                self.info("Harga/Stok harus berupa angka!")
                return
            
            if product:
                self.db.update_product(product['id'], name, price, stock)
            else:
                self.db.add_product(name, price, stock)
            
            popup.dismiss()
            self.refresh_all()

        btn_save.bind(on_release=save)
        content.add_widget(btn_save)
        popup.open()

    def refresh_history_list(self):
        container = self.root.ids.history_list
        container.clear_widgets()
        sales = self.db.get_sales()
        
        total_omset = sum(s['total_amount'] for s in sales)
        self.root.ids.history_total_label.text = f"Total Omset: {self.money(total_omset)}"

        for s in sales:
            row = Button(size_hint_y=None, height=dp(40), background_normal='', background_color=(1, 1, 1, 1))
            
            box = BoxLayout(spacing=dp(6))
            box.add_widget(Label(text=s['invoice_no'], font_size='11sp', color=(0.1, 0.1, 0.1, 1), size_hint_x=0.4))
            box.add_widget(Label(text=self.money(s['total_amount']), font_size='11sp', bold=True, color=(0.12, 0.45, 0.88, 1), size_hint_x=0.3))
            box.add_widget(Label(text=s['created_at'][:16], font_size='10sp', color=(0.5, 0.5, 0.5, 1), size_hint_x=0.3))
            
            row.add_widget(box)
            row.bind(on_release=lambda x, sale=s: self.open_sale_detail_modal(sale))
            container.add_widget(row)

    def open_sale_detail_modal(self, sale):
        items = self.db.get_sale_items(sale['id'])
        content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(6))
        
        content.add_widget(Label(text=f"Faktur: {sale['invoice_no']}", bold=True, size_hint_y=None, height=dp(20)))
        content.add_widget(Label(text=f"Total: {self.money(sale['total_amount'])} | Bayar: {self.money(sale['paid_amount'])}", size_hint_y=None, height=dp(20)))
        
        scroll = ScrollView()
        item_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(4))
        item_box.bind(minimum_height=item_box.setter('height'))
        
        formatted_items = []
        for it in items:
            line = f"{it['product_name']} x{it['quantity']} = {self.money(it['subtotal'])}"
            item_box.add_widget(Label(text=line, font_size='12sp', size_hint_y=None, height=dp(24)))
            formatted_items.append({
                'name': it['product_name'],
                'qty': it['quantity'],
                'price': it['price'],
                'line_total': it['subtotal']
            })

        scroll.add_widget(item_box)
        content.add_widget(scroll)

        popup = Popup(title="Detail Transaksi", content=content, size_hint=(0.85, 0.6))
        
        btn_box = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(36))
        btn_reprint = Button(text="CETAK RE-PRINT", background_normal='', background_color=(0.12, 0.45, 0.88, 1))
        
        def reprint(x):
            if not self.bt_mac_address.strip():
                self.info("Printer Bluetooth belum dikonfigurasi!")
                return
            receipt_text = self.generate_receipt_text(
                sale['invoice_no'], 
                formatted_items, 
                sale['total_amount'], 
                sale['paid_amount'], 
                sale['change_amount'],
                date_str=sale['created_at'][:16]
            )
            printed, msg = ThermalPrinterManager.print_receipt(self.bt_mac_address.strip(), receipt_text)
            self.info(msg)

        btn_reprint.bind(on_release=reprint)
        btn_box.add_widget(btn_reprint)
        content.add_widget(btn_box)
        
        popup.open()

    def info(self, message):
        popup = Popup(
            title="Informasi",
            content=Label(text=message, halign='center', valign='middle'),
            size_hint=(0.75, 0.3)
        )
        popup.open()

if __name__ == '__main__':
    POSApp().run()
