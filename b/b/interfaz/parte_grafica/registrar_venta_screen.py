from kivy.uix.screenmanager import Screen
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivy.metrics import dp
from clases.venta import Venta
from clases.detalle_venta import DetalleVenta
from clases.conexion import crear_conexion

#aca creamos la clase donde registarremos las ventas que se hagan
class registrarVenta(Screen):
    def on_enter(self):
        if hasattr(self, "formulario_creado") and self.formulario_creado:
            return
        
        layout = MDBoxLayout(orientation="vertical", spacing=20, padding=20)

        layout.add_widget(MDLabel(
            text="Registrar venta",
            halign="center",
            theme_text_color="Primary",
            font_style="H5",
            size_hint_y=None,
            height=dp(70)
        ))

        # aca estan los campos del formulario que se deben llenar (la fecha se cambiara, por ahora lo deje asi)
        self.campo_producto = MDTextField(hint_text="ID Producto")
        self.campo_cantidad = MDTextField(hint_text="Cantidad", input_filter="int")
        self.campo_precio_unitario = MDTextField(hint_text="Precio unitario", input_filter="float")
        self.campo_fecha = MDTextField(hint_text="Fecha (YYYY-MM-DD, opcional)")

        layout.add_widget(self.campo_producto)
        layout.add_widget(self.campo_cantidad)
        layout.add_widget(self.campo_precio_unitario)
        layout.add_widget(self.campo_fecha)

        # aca estan los botones donde cada uno tiene un parametro si es tocado, luego mads adelante esta el direcionamiento
        botones = MDBoxLayout(size_hint=(1, None), height=dp(60), spacing=20, padding=[0,10,0,0])
        botones.add_widget(MDRaisedButton(text="Registrar venta", on_release=lambda x: self.registrar_venta()))
        botones.add_widget(MDRaisedButton(text="Volver", on_release=lambda x: self.volver_inicio()))
        layout.add_widget(botones)

        #estas serian las ventas que se añaden segun lo que necesite
        self.add_widget(layout)
        self.formulario_creado = True

    #luego de crear todo lo "visual vamos por la conexion con la bdd"
    def registrar_venta(self):
        # aca creamos la venta
        venta = Venta()
        id_venta = venta.registrar()
        if not id_venta:
            print("No se pudo crear la venta")
            return

        # aca se crea los detalles de venta osea cada campo con cada atributo y su dato
        detalle = DetalleVenta(None, float(self.campo_precio_unitario.text), int(self.campo_producto.text), id_venta, int(self.campo_cantidad.text))
        detalle_data = [{"id_product": int(self.campo_producto.text), "cantidad": int(self.campo_cantidad.text), "precio_unitario": float(self.campo_precio_unitario.text)}]
        detalle.registrar_venta(id_venta, detalle_data)

        # limpiamos luego de usar
        self.campo_producto.text = ""
        self.campo_cantidad.text = ""
        self.campo_precio_unitario.text = ""
        self.campo_fecha.text = ""

        # Volver a la pantalla de ventas
        self.manager.current = "ventas"

    def volver_inicio(self):
        self.manager.current = "ventas"
