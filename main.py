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

<TitleLabel@Label>:
    font_size: "22sp"
    bold: True
    color: .07,.09,.13,1
    size_hint_y: None
    height: dp(42)
    halign: "left"
    valign: "middle"
    text_size: self.size

<SectionLabel@Label>:
    font_size: "15sp"
    bold: True
    color: .08,.10,.14,1
    size_hint_y: None
    height: dp(30)
    halign: "left"
    valign: "middle"
    text_size: self.size

<SmallLabel@Label>:
    font_size: "11sp"
    color: .42,.46,.52,1

<NavButton@Button>:
    background_normal: ""
    background_color: .99,.99,1,1
    color: .30,.34,.40,1
    font_size: "9sp"
    bold: True
    padding: dp(2), dp(2)
    halign: "center"
    valign: "middle"
    text_size: self.size
    canvas.before:
        Color:
            rgba: .88,.91,.95,1
        Line:
            width: 1
            rounded_rectangle: self.x, self.y, self.width, self.height, dp(8)

<PrimaryButton@Button>:
    size_hint_y: None
    height: dp(50)
    background_normal: ""
    background_color: .05,.58,.31,1
    color: 1,1,1,1
    font_size: "14sp"
    bold: True
    canvas.before:
        Color:
            rgba: .05,.58,.31,1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10),dp(10),dp(10),dp(10)]

<DarkButton@Button>:
    size_hint_y: None
    height: dp(48)
    background_normal: ""
    background_color: .08,.10,.14,1
    color: 1,1,1,1
    bold: True
    canvas.before:
        Color:
            rgba: .08,.10,.14,1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10),dp(10),dp(10),dp(10)]

<RootLayout>:
    orientation: "vertical"
    canvas.before:
        Color:
            rgba: .95,.96,.98,1
        Rectangle:
            pos: self.pos
            size: self.size

    # HEADER
    BoxLayout:
        size_hint_y: None
        height: dp(62)
        padding: dp(14),dp(7)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: .035,.055,.09,1
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: "â˜°"
            size_hint_x: None
            width: dp(34)
            font_size: "25sp"
            color: 1,1,1,1
            halign: "center"
            valign: "middle"
            text_size: self.size

        Label:
            text: app.store_name
            font_size: "19sp"
            bold: True
            color: 1,1,1,1
            halign: "left"
            valign: "middle"
            text_size: self.size

        Label:
            text: "POS v" + app.version
            size_hint_x: None
            width: dp(78)
            font_size: "11sp"
            color: .70,.74,.82,1
            halign: "right"
            valign: "middle"
            text_size: self.size

    # MOBILE NAVIGATION
    BoxLayout:
        size_hint_y: None
        height: dp(62)
        padding: dp(5),dp(5)
        spacing: dp(4)
        canvas.before:
            Color:
                rgba: 1,1,1,1
            Rectangle:
                pos: self.pos
                size: self.size

        NavButton:
            text: "âŒ‚\nDashboard"
            on_release: app.show_screen("dashboard")
        NavButton:
            text: "â–£\nKasir / POS"
            on_release: app.show_screen("pos")
        NavButton:
            text: "â–¤\nProduk"
            on_release: app.show_screen("products")
        NavButton:
            text: "â—·\nRiwayat"
            on_release: app.show_screen("history")
        NavButton:
            text: "â–¥\nLaporan"
            on_release: app.show_screen("reports")
        NavButton:
            text: "âš™\nPengaturan"
            on_release: app.show_screen("settings")

    ScreenManager:
        id: sm

        # ================= DASHBOARD =================
        Screen:
            name: "dashboard"
            ScrollView:
                do_scroll_x: False
                BoxLayout:
                    orientation: "vertical"
                    padding: dp(14)
                    spacing: dp(10)
                    size_hint_y: None
                    height: self.minimum_height

                    TitleLabel:
                        text: "Dashboard"

                    SmallLabel:
                        text: "Ringkasan aktivitas toko hari ini"
                        size_hint_y: None
                        height: dp(24)

                    GridLayout:
                        cols: 2
                        spacing: dp(9)
                        size_hint_y: None
                        height: dp(150)

                        BoxLayout:
                            orientation: "vertical"
                            padding: dp(12)
                            spacing: dp(2)
                            canvas.before:
                                Color:
                                    rgba: .86,.97,.91,1
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [dp(12),dp(12),dp(12),dp(12)]
                            Label:
                                text: "PENJUALAN"
                                font_size: "10sp"
                                bold: True
                                color: .10,.42,.25,1
                                halign: "left"
                                text_size: self.size
                            Label:
                                id: dash_sales
                                text: "Rp 0"
                                font_size: "20sp"
                                bold: True
                                color: .04,.45,.23,1
                                halign: "left"
                                valign: "middle"
                                text_size: self.size

                        BoxLayout:
                            orientation: "vertical"
                            padding: dp(12)
                            spacing: dp(2)
                            canvas.before:
                                Color:
                                    rgba: .88,.94,1,1
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [dp(12),dp(12),dp(12),dp(12)]
                            Label:
                                text: "TRANSAKSI"
                                font_size: "10sp"
                                bold: True
                                color: .15,.35,.62,1
                                halign: "left"
                                text_size: self.size
                            Label:
                                id: dash_trx
                                text: "0"
                                font_size: "20sp"
                                bold: True
                                color: .10,.28,.55,1
                                halign: "left"
                                valign: "middle"
                                text_size: self.size

                        BoxLayout:
                            orientation: "vertical"
                            padding: dp(12)
                            spacing: dp(2)
                            canvas.before:
                                Color:
                                    rgba: 1,.94,.84,1
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [dp(12),dp(12),dp(12),dp(12)]
                            Label:
                                text: "PRODUK AKTIF"
                                font_size: "10sp"
                                bold: True
                                color: .58,.38,.06,1
                                halign: "left"
                                text_size: self.size
                            Label:
                                id: dash_products
                                text: "0"
                                font_size: "20sp"
                                bold: True
                                color: .50,.30,.03,1
                                halign: "left"
                                valign: "middle"
                                text_size: self.size

                        BoxLayout:
                            orientation: "vertical"
                            padding: dp(12)
                            spacing: dp(2)
                            canvas.before:
                                Color:
                                    rgba: .94,.90,1,1
                                RoundedRectangle:
                                    pos: self.pos
                                    size: self.size
                                    radius: [dp(12),dp(12),dp(12),dp(12)]
                            Label:
                                text: "STOK MENIPIS"
                                font_size: "10sp"
                                bold: True
                                color: .45,.25,.68,1
                                halign: "left"
                                text_size: self.size
                            Label:
                                id: dash_low
                                text: "0"
                                font_size: "20sp"
                                bold: True
                                color: .40,.20,.65,1
                                halign: "left"
                                valign: "middle"
                                text_size: self.size

                    BoxLayout:
                        size_hint_y: None
                        height: dp(210)
                        orientation: "vertical"
                        padding: dp(12)
                        spacing: dp(5)
                        canvas.before:
                            Color:
                                rgba: 1,1,1,1
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [dp(12),dp(12),dp(12),dp(12)]

                        Label:
                            text: "PENJUALAN 7 HARI TERAKHIR"
                            size_hint_y: None
                            height: dp(25)
                            font_size: "12sp"
                            bold: True
                            color: .10,.13,.18,1
                            halign: "left"
                            text_size: self.size

                        GridLayout:
                            id: dashboard_chart
                            cols: 7
                            spacing: dp(7)
                            padding: dp(5),dp(5)
                            size_hint_y: None
                            height: dp(145)

                    DarkButton:
                        text: "REFRESH DASHBOARD"
                        on_release: app.refresh_all()

        # ================= POS =================
        Screen:
            name: "pos"
            ScrollView:
                do_scroll_x: False
                BoxLayout:
                    orientation: "vertical"
                    padding: dp(12)
                    spacing: dp(10)
                    size_hint_y: None
                    height: self.minimum_height

                    BoxLayout:
                        size_hint_y: None
                        height: dp(35)
                        spacing: dp(6)

                        Label:
                            text: "PILIH PRODUK"
                            font_size: "20sp"
                            bold: True
                            color: .07,.09,.13,1
                            halign: "left"
                            text_size: self.size

                        Label:
                            text: "Tap + untuk menambah"
                            font_size: "10sp"
                            color: .48,.51,.56,1
                            size_hint_x: None
                            width: dp(115)
                            halign: "right"
                            valign: "middle"
                            text_size: self.size

                    BoxLayout:
                        size_hint_y: None
                        height: dp(50)
                        spacing: dp(7)

                        TextInput:
                            id: search_pos
                            hint_text: "Cari nama / barcode produk..."
                            multiline: False
                            padding: dp(12),dp(12)
                            font_size: "13sp"
                            background_normal: ""
                            background_color: 1,1,1,1
                            on_text: app.refresh_pos_products(self.text)

                        Button:
                            text: "âŒ•"
                            size_hint_x: None
                            width: dp(52)
                            font_size: "22sp"
                            background_normal: ""
                            background_color: .08,.55,.30,1
                            color: 1,1,1,1

                    BoxLayout:
                        size_hint_y: None
                        height: dp(40)
                        spacing: dp(6)

                        Button:
                            text: "SEMUA"
                            background_normal: ""
                            background_color: .05,.58,.31,1
                            color: 1,1,1,1
                            bold: True
                        Button:
                            text: "MINUMAN"
                            background_normal: ""
                            background_color: .91,.93,.96,1
                            color: .25,.28,.34,1
                        Button:
                            text: "MAKANAN"
                            background_normal: ""
                            background_color: .91,.93,.96,1
                            color: .25,.28,.34,1
                        Button:
                            text: "LAINNYA"
                            background_normal: ""
                            background_color: .91,.93,.96,1
                            color: .25,.28,.34,1

                    GridLayout:
                        id: product_grid
                        cols: 2
                        spacing: dp(8)
                        size_hint_y: None
                        height: self.minimum_height

                    BoxLayout:
                        orientation: "vertical"
                        size_hint_y: None
                        height: dp(390)
                        padding: dp(12)
                        spacing: dp(7)
                        canvas.before:
                            Color:
                                rgba: 1,1,1,1
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [dp(12),dp(12),dp(12),dp(12)]

                        BoxLayout:
                            size_hint_y: None
                            height: dp(32)

                            Label:
                                text: "KERANJANG BELANJA"
                                font_size: "16sp"
                                bold: True
                                color: .08,.10,.14,1
                                halign: "left"
                                text_size: self.size

                            Button:
                                text: "Kosongkan"
                                size_hint_x: None
                                width: dp(82)
                                background_normal: ""
                                background_color: 0,0,0,0
                                color: .85,.18,.18,1
                                font_size: "11sp"
                                on_release: app.cart.clear(); app.refresh_cart()

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
                            height: dp(100)

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
                                font_size: "17sp"
                                bold: True
                                halign: "left"
                                text_size: self.size
                            Label:
                                id: pos_total
                                text: "Rp 0"
                                font_size: "18sp"
                                bold: True
                                color: .04,.50,.25,1
                                halign: "right"
                                text_size: self.size

                    BoxLayout:
                        orientation: "vertical"
                        size_hint_y: None
                        height: dp(180)
                        padding: dp(12)
                        spacing: dp(7)
                        canvas.before:
                            Color:
                                rgba: 1,1,1,1
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [dp(12),dp(12),dp(12),dp(12)]

                        Label:
                            text: "PEMBAYARAN"
                            size_hint_y: None
                            height: dp(27)
                            font_size: "15sp"
                            bold: True
                            halign: "left"
                            text_size: self.size

              
