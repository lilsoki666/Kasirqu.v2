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
from kivy.uix.spinner import Spinner
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

                SectionLabel:
                    text: "Riwayat Penjualan"

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

                    Label:
                        text: "Ukuran Kertas Struk:"
                        font_size: "12sp"
                        color: 0.10, 0.14, 0.20, 1
                        size_hint_y: None
                        height: dp(20)
                        halign: "left"
                        valign: "middle"
                        text_size: self.size

                    Spinner:
                        id: setting_paper_width
                        text: "80mm"
                        values: ["80mm", "58mm"]
                        size_hint_y: None
                        height: dp(40)

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
    paper_width = StringProperty("80mm")

    cart = ListProperty([])
    cart_total = NumericProperty(0)

    def build(self):
        self.db = Database()
        root = Builder.load_string(KV)
        self.load_settings(root)
        return root

    def on_start(self):
        self.refresh_all()

    def money(self, val):
        try:
            return f"Rp {float(val):,.0f}".replace(",", ".")
        except:
            return "Rp 0"

    def load_settings(self, root_widget=None):
        self.store_name = self.db.get_setting("store_name", "TOKO SAYA")
        self.store_address = self.db.get_setting("store_address", "")
        self.tax_percent = self.db.get_setting("tax_percent", "0")
        self.cashier_name = self.db.get_setting("cashier_name", "Admin")
        self.bt_mac_address = self.db.get_setting("bt_mac_address", "")
        self.paper_width = self.db.get_setting("paper_width", "80mm")
        
        r = root_widget or self.root
        if r and hasattr(r, 'ids') and 'setting_paper_width' in r.ids:
            r.ids.setting_paper_width.text = self.paper_width

    def save_settings(self):
        ids = self.root.ids
        self.db.set_setting("store_name", ids.setting_store.text.strip() or "TOKO SAYA")
        self.db.set_setting("store_address", ids.setting_address.text.strip())
        self.db.set_setting("cashier_name", ids.setting_cashier.text.strip() or "Admin")
        self.db.set_setting("bt_mac_address", ids.setting_bt_mac.text.strip())
        self.db.set_setting("paper_width", ids.setting_paper_width.text)
        
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
            'line_total': product['price']
        })
        self.update_cart_ui()

    def update_cart_ui(self):
        container = self.root.ids.cart_list
        container.clear_widgets()
        total = 0

        for idx, item in enumerate(self.cart):
            total += item['line_total']
            row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(4))
            row.add_widget(Label(text=item['name'], font_size='11sp', color=(0.1, 0.1, 0.1, 1), size_hint_x=0.4))
            row.add_widget(Label(text=f"{item['qty']}x", font_size='11sp', color=(0.3, 0.3, 0.3, 1), size_hint_x=0.2))
            row.add_widget(Label(text=self.money(item['line_total']), font_size='11sp', color=(0.1, 0.1, 0.1, 1), size_hint_x=0.3))
            
            del_btn = Button(text="X", size_hint_x=0.1, background_normal='', background_color=(0.9, 0.3, 0.3, 1), color=(1,1,1,1))
            del_btn.bind(on_release=lambda x, i=idx: self.remove_cart_item(i))
            row.add_widget(del_btn)
            
            container.add_widget(row)

        self.cart_total = total

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

        popup = Popup(title="Pembayaran", content=content, size_hint=(0.85, 0.45))

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

    def generate_receipt_text(self, invoice, cart_items, total, paid, change):
        lines = []
        # Secara bawaan menggunakan 80mm (48 karakter)
        LINE_WIDTH = 48 if self.paper_width == "80mm" else 32
        
        lines.append(self.store_name.center(LINE_WIDTH))
        if self.store_address:
            lines.append(self.store_address.center(LINE_WIDTH))
            
        lines.append("-" * LINE_WIDTH)
        lines.append(f"No  : {invoice}")
        lines.append(f"Tgl : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
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
        
        lbl_w = 12 if LINE_WIDTH == 32 else 15
        lines.append("Total  :".ljust(lbl_w) + tot_str.rjust(LINE_WIDTH - lbl_w))
        lines.append("Bayar  :".ljust(lbl_w) + paid_str.rjust(LINE_WIDTH - lbl_w))
        lines.append("Kembali:".ljust(lbl_w) + change_str.rjust(LINE_WIDTH - lbl_w))
        
        lines.append("-" * LINE_WIDTH)
        lines.append("Terima Kasih Atas Kunjungan Anda!".center(LINE_WIDTH))
        
        return "\n".join(lines)

    def refresh_product_list(self, query=""):
        container = self.root.ids.product_crud_list
        container.clear_widgets()
        products = self.db.get_products(query)
        for p in products:
            row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
            row.add_widget(Label(text=p['name'], font_size='12sp', color=(0.1, 0.1, 0.1, 1), size_hint_x=0.4))
            row.add_widget(Label(text=self.money(p['price']), font_size='12sp', color=(0.1, 0.1, 0.1, 1), size_hint_x=0.25))
            row.add_widget(Label(text=f"Stok: {p['stock']}", font_size='12sp', color=(0.3, 0.3, 0.3, 1), size_hint_x=0.15))
            
            btn_edit = Button(text="Edit", size_hint_x=0.1, background_normal='', background_color=(0.12, 0.45, 0.88, 1))
            btn_edit.bind(on_release=lambda x, prod=p: self.open_product_modal(prod))
            row.add_widget(btn_edit)
            
            container.add_widget(row)

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
        for s in sales:
            row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(6))
            row.add_widget(Label(text=s['invoice_no'], font_size='11sp', color=(0.1, 0.1, 0.1, 1), size_hint_x=0.4))
            row.add_widget(Label(text=self.money(s['total_amount']), font_size='11sp', bold=True, color=(0.12, 0.45, 0.88, 1), size_hint_x=0.3))
            row.add_widget(Label(text=s['created_at'][:16], font_size='10sp', color=(0.5, 0.5, 0.5, 1), size_hint_x=0.3))
            container.add_widget(row)

    def info(self, message):
        popup = Popup(
            title="Informasi",
            content=Label(text=message, halign='center', valign='middle'),
            size_hint=(0.75, 0.3)
        )
        popup.open()

if __name__ == '__main__':
    POSApp().run()
