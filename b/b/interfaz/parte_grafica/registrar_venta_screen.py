from kivy.uix.screenmanager import Screen
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from clases.venta import Venta
from clases.detalle_venta import DetalleVenta
from clases.conexion import crear_conexion

class registrarVenta(Screen):
    # aca esta la variable donde determina lo maximo de cada
    MAX_CANTIDAD = 100          
    MAX_PRECIO = 250000

    def on_enter(self):
        # si ya creamos el formulario no lo volvemos a crear
        if hasattr(self, "formulario_creado") and self.formulario_creado:
            return

        layout = MDBoxLayout(orientation="vertical", spacing=20, padding=20)

        # título de la pantalla
        layout.add_widget(MDLabel(
            text="Registrar venta",
            halign="center",
            theme_text_color="Primary",
            font_style="H5",
            size_hint_y=None,
            height=dp(70)
        ))

        # menú desplegable de productos
        self.productos = self.obtener_productos()   # traemos productos de la BDD
        self.id_producto_seleccionado = None
        self.boton_producto = MDRaisedButton(
            text="Seleccionar producto",
            on_release=self.abrir_menu_productos
        )
        layout.add_widget(self.boton_producto)

        # campos de cantidad y precio
        self.campo_cantidad = MDTextField(hint_text="Cantidad", input_filter="int")
        self.campo_precio_unitario = MDTextField(hint_text="Precio unitario", input_filter="int")
        layout.add_widget(self.campo_cantidad)
        layout.add_widget(self.campo_precio_unitario)

        # botones registrar y volver
        botones = MDBoxLayout(size_hint=(1, None), height=dp(60), spacing=20, padding=[0,10,0,0])
        botones.add_widget(MDRaisedButton(text="Registrar venta", on_release=self.confirmar_registro))
        botones.add_widget(MDRaisedButton(text="Volver", on_release=lambda x: self.volver_ventas()))
        layout.add_widget(botones)

        self.add_widget(layout)
        self.formulario_creado = True  # marcamos que ya creamos el formulario

    def volver_ventas(self):
        # vuelve a la pantalla de ventas
        self.manager.current = "ventas"

    def obtener_productos(self):
        # trae los productos de la base de datos
        conexion = crear_conexion()
        productos = []
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("SELECT id, nombre FROM producto")
                for id_prod, nombre in cursor.fetchall():
                    productos.append({"id": id_prod, "nombre": nombre})
            except Exception as e:
                self.mostrar_error(f"Error al obtener productos: {e}")
            finally:
                cursor.close()
                conexion.close()
        return productos

    def abrir_menu_productos(self, instance):
        # abre el menú desplegable con los productos
        menu_items = [
            {"text": p["nombre"], "viewclass": "OneLineListItem", "on_release": lambda x=p: self.seleccionar_producto(x)}
            for p in self.productos
        ]
        self.menu = MDDropdownMenu(caller=instance, items=menu_items, width_mult=4)
        self.menu.open()

    def seleccionar_producto(self, producto):
        # selecciona un producto del menú y actualiza el botón
        self.id_producto_seleccionado = producto["id"]
        self.boton_producto.text = f"Producto: {producto['nombre']}"
        self.menu.dismiss()

    def confirmar_registro(self, instance):
        # valida que todo esté bien antes de registrar la venta
        if not self.id_producto_seleccionado:
            self.mostrar_error("Debe seleccionar un producto.")
            return

        if not self.campo_cantidad.text or not self.campo_precio_unitario.text:
            self.mostrar_error("Debe completar todos los campos.")
            return

        # validación cantidad
        cantidad_text = self.campo_cantidad.text
        if not cantidad_text.isdigit() or cantidad_text.startswith("0"):
            self.mostrar_error("Cantidad inválida: no se permiten ceros iniciales ni valores no numéricos.")
            return
        cantidad = int(cantidad_text)
        if cantidad <= 0 or cantidad > self.MAX_CANTIDAD:
            self.mostrar_error(f"Cantidad inválida. Máximo permitido: {self.MAX_CANTIDAD}.")
            return

        # validación precio
        precio_text = self.campo_precio_unitario.text
        if not precio_text.isdigit():
            self.mostrar_error("Precio inválido: debe ser un número entero.")
            return
        precio = int(precio_text)
        if precio < 1 or precio > self.MAX_PRECIO:
            self.mostrar_error(f"Precio inválido. Debe estar entre 1 y {self.MAX_PRECIO}.")
            return

        # confirmación antes de registrar
        self.dialog = MDDialog(
            text=f"¿Desea registrar esta venta?\nCantidad: {cantidad}\nPrecio: {precio}",
            buttons=[
                MDFlatButton(text="Cancelar", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="Registrar", on_release=self.registrar_venta)
            ],
            auto_dismiss=False
        )
        self.dialog.open()

    def registrar_venta(self, instance):
        # guarda la venta y el detalle en la BDD
        self.dialog.dismiss()
        try:
            venta = Venta()
            id_venta = venta.registrar()
            if not id_venta:
                self.mostrar_error("No se pudo crear la venta")
                return

            detalle = DetalleVenta(
                None,
                int(self.campo_precio_unitario.text),
                self.id_producto_seleccionado,
                id_venta,
                int(self.campo_cantidad.text)
            )
            detalle_data = [{"id_product": self.id_producto_seleccionado,
                             "cantidad": int(self.campo_cantidad.text),
                             "precio_unitario": int(self.campo_precio_unitario.text)}]
            detalle.registrar_venta(id_venta, detalle_data)

            # limpiar campos para la próxima venta
            self.id_producto_seleccionado = None
            self.boton_producto.text = "Seleccionar producto"
            self.campo_cantidad.text = ""
            self.campo_precio_unitario.text = ""

            # volvemos a pantalla de ventas
            self.manager.current = "ventas"
        except Exception as e:
            self.mostrar_error(f"Error al registrar venta: {e}")

    def mostrar_error(self, mensaje):
        # muestra un popup con el error
        self.dialog_error = MDDialog(
            text=mensaje,
            buttons=[MDFlatButton(text="Cerrar", on_release=lambda x: self.dialog_error.dismiss())]
        )
        self.dialog_error.open()
