from kivy.uix.screenmanager import Screen
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from clases.conexion import crear_conexion
from kivymd.uix.menu import MDDropdownMenu

# se crea la clase para manejar la tabla y ciertas funciones de ventas
class ventasScreen(Screen):
    # límites para cantidad y precio, para que no entren cosas raras
    MAX_CANTIDAD = 100
    MAX_PRECIO = 250000.0  # precio máximo permitido, mínimo 1 peso

    # cuando entras a la pantalla, creamos la interfaz y cargamos los datos
    def on_enter(self):
        self.crear_interfaz()
        self.cargar_datos()
        self.id_seleccionado = None  # variable que guarda el id de la venta seleccionada

    # aca creamos la tabla tipo Excel y los botones que vamos a usar
    def crear_interfaz(self):
        if hasattr(self, "interfaz_creada") and self.interfaz_creada:
            return

        layout_principal = MDBoxLayout(orientation="vertical", spacing=20, padding=20)

        titulo = MDLabel(
            text="Gestión de Ventas",
            halign="center",
            theme_text_color="Primary",
            font_style="H5",
            size_hint_y=None,
            height=dp(40)
        )

        # la tabla con columnas que muestran ID, Producto, Cantidad, Precio y Fecha
        self.tabla = MDDataTable(
            size_hint=(1, 0.8),
            use_pagination=True,
            rows_num=10,
            column_data=[
                ("ID Venta", dp(25)),
                ("Producto", dp(40)),
                ("Cantidad", dp(30)),
                ("Precio por unidad", dp(40)),
                ("Fecha de la venta", dp(40))
            ],
            row_data=[]
        )
        self.tabla.bind(on_row_press=self.seleccionar_fila)  # para saber cuál fila se selecciona

        # aca ponemos los botones de la pantalla
        botones = MDBoxLayout(size_hint=(1, None), height=dp(60), spacing=15)
        botones.add_widget(MDRaisedButton(
            text="Registrar venta",
            on_release=lambda x: setattr(self.manager, "current", "registrar_venta")
        ))
        botones.add_widget(MDRaisedButton(text="Modificar venta", on_release=self.abrir_popup_mod))
        botones.add_widget(MDRaisedButton(text="Eliminar venta", on_release=self.confirmar_eliminar))
        botones.add_widget(MDRaisedButton(text="Volver al inicio", on_release=self.volver_inicio))

        layout_principal.add_widget(titulo)
        layout_principal.add_widget(self.tabla)
        layout_principal.add_widget(botones)
        self.add_widget(layout_principal)

        self.interfaz_creada = True  # para que no vuelva a crear todo si entras otra vez

    # aca cargamos los datos de la base para que se vean en la tabla
    def cargar_datos(self):
        conexion = crear_conexion()
        if not conexion:
            self.mostrar_error("No se pudo conectar a la base de datos")
            return
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT v.id, p.nombre, d.cantidad, d.precio_unitario, v.fecha_venta
                FROM ventas v
                JOIN detalle_venta d ON v.id = d.id_ventas
                JOIN producto p ON d.id_product = p.id
                ORDER BY v.id DESC
            """)
            datos = cursor.fetchall()
            self.tabla.row_data = [
                (str(row[0]), str(row[1]), str(row[2]), str(row[3]), str(row[4]))
                for row in datos
            ]
        except Exception as e:
            self.mostrar_error(f"Error al cargar los datos: {e}")
        finally:
            cursor.close()
            conexion.close()

    # aca seleccionamos la fila en la tabla y guardamos el id
    def seleccionar_fila(self, instance_table, instance_row):
        try:
            fila = instance_row.text.split(", ")
            self.id_seleccionado = fila[0]
        except Exception as e:
            self.mostrar_error(f"Error al seleccionar la fila: {e}")

    # aca preguntamos si de verdad quieres eliminar la venta
    def confirmar_eliminar(self, instance):
        if not self.id_seleccionado:
            self.mostrar_error("No se ha seleccionado ninguna venta para eliminar")
            return
        self.dialog = MDDialog(
            text=f"¿Está seguro que desea eliminar la venta {self.id_seleccionado}?",
            buttons=[
                MDFlatButton(text="Cancelar", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="Eliminar", on_release=self.eliminar_venta)
            ],
            auto_dismiss=False
        )
        self.dialog.open()

    # aca eliminamos la venta y su detalle de la base
    def eliminar_venta(self, instance):
        self.dialog.dismiss()
        conexion = crear_conexion()
        if not conexion:
            self.mostrar_error("No se pudo conectar a la base de datos")
            return
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM detalle_venta WHERE id_ventas=%s", (self.id_seleccionado,))
            cursor.execute("DELETE FROM ventas WHERE id=%s", (self.id_seleccionado,))
            conexion.commit()
            self.cargar_datos()
        except Exception as e:
            conexion.rollback()
            self.mostrar_error(f"Error al eliminar la venta: {e}")
        finally:
            cursor.close()
            conexion.close()

    # aca abrimos un popup para modificar la venta seleccionada
    def abrir_popup_mod(self, instance):
        if not self.id_seleccionado:
            self.mostrar_error("No se ha seleccionado ninguna venta para modificar")
            return

        conexion = crear_conexion()
        if not conexion:
            self.mostrar_error("No se pudo conectar a la base de datos")
            return

        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT p.nombre, d.cantidad, d.precio_unitario
                FROM detalle_venta d
                JOIN producto p ON d.id_product = p.id
                WHERE d.id_ventas = %s LIMIT 1
            """, (self.id_seleccionado,))
            venta = cursor.fetchone()
            if not venta:
                self.mostrar_error("No se encontró el detalle de la venta")
                return

            nombre_producto, cantidad, precio_unitario = venta
            cursor.execute("SELECT nombre FROM producto ORDER BY nombre ASC")
            productos = [row[0] for row in cursor.fetchall()]

            contenido = MDBoxLayout(orientation="vertical", spacing=dp(10), padding=dp(15), size_hint_y=None)
            contenido.height = dp(250)

            # aca guardamos el producto seleccionado y armamos el menu desplegable
            self.producto_seleccionado = nombre_producto
            self.boton_producto = MDRaisedButton(text=nombre_producto, size_hint_y=None, height=dp(40))
            menu_items = [{"text": p, "on_release": lambda x=p: self.seleccionar_producto_mod(x)} for p in productos]
            self.menu_productos = MDDropdownMenu(caller=self.boton_producto, items=menu_items, width_mult=4)

            # aca ponemos los inputs de cantidad y precio
            self.input_cantidad = MDTextField(text=str(cantidad), hint_text="Cantidad", input_filter="int")
            self.input_precio = MDTextField(text=str(precio_unitario), hint_text="Precio Unitario", input_filter="int")

            contenido.add_widget(MDLabel(text="Producto:", halign="left"))
            contenido.add_widget(self.boton_producto)
            contenido.add_widget(MDLabel(text="Cantidad:", halign="left"))
            contenido.add_widget(self.input_cantidad)
            contenido.add_widget(MDLabel(text="Precio Unitario:", halign="left"))
            contenido.add_widget(self.input_precio)

            # aca el popup final
            self.dialog = MDDialog(
                type="custom",
                content_cls=contenido,
                buttons=[
                    MDFlatButton(text="Cancelar", on_release=lambda x: self.dialog.dismiss()),
                    MDRaisedButton(text="Guardar", on_release=self.confirmar_modificacion)
                ],
                auto_dismiss=False
            )
            self.dialog.open()
            self.boton_producto.bind(on_release=lambda x: self.menu_productos.open())
        except Exception as e:
            self.mostrar_error(f"Error al abrir popup de modificación: {e}")
        finally:
            cursor.close()
            conexion.close()

    # aca se selecciona un producto dentro del popup
    def seleccionar_producto_mod(self, nombre):
        self.producto_seleccionado = nombre
        self.boton_producto.text = nombre
        self.menu_productos.dismiss()

    # aca validamos los datos y mostramos mensaje de confirmacion antes de guardar
    def confirmar_modificacion(self, instance):
        cantidad_text = self.input_cantidad.text
        precio_text = self.input_precio.text

        # validacion cantidad: entero positivo y maximo permitido
        if not cantidad_text.isdigit() or cantidad_text.startswith("0"):
            self.mostrar_error("Cantidad inválida: no se permiten ceros iniciales ni valores no numéricos.")
            return
        cantidad = int(cantidad_text)
        if cantidad <= 0 or cantidad > self.MAX_CANTIDAD:
            self.mostrar_error(f"Cantidad inválida. Máximo permitido: {self.MAX_CANTIDAD}.")
            return

        # validacion precio: entero entre 1 y MAX_PRECIO
        try:
            precio = int(precio_text)
            if precio < 1 or precio > self.MAX_PRECIO:
                raise ValueError
        except:
            self.mostrar_error(f"Precio inválido. Debe ser un entero entre 1 y {int(self.MAX_PRECIO)}")
            return

        # confirmacion antes de guardar cambios
        self.dialog.dismiss()
        self.dialog = MDDialog(
            text=f"¿Desea guardar los cambios de la venta {self.id_seleccionado}?",
            buttons=[
                MDFlatButton(text="Cancelar", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="Guardar", on_release=self.guardar_modificacion)
            ],
            auto_dismiss=False
        )
        self.dialog.open()

    # aca se guardan los cambios definitivos en la base
    def guardar_modificacion(self, instance):
        self.dialog.dismiss()
        nuevo_nombre = self.producto_seleccionado
        nueva_cantidad = int(self.input_cantidad.text)
        nuevo_precio = int(self.input_precio.text)

        conexion = crear_conexion()
        if not conexion:
            self.mostrar_error("No se pudo conectar a la base de datos")
            return
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id FROM producto WHERE nombre=%s LIMIT 1", (nuevo_nombre,))
            producto = cursor.fetchone()
            if not producto:
                self.mostrar_error("Producto no encontrado.")
                return
            id_producto = producto[0]
            cursor.execute("""
                UPDATE detalle_venta
                SET id_product=%s, cantidad=%s, precio_unitario=%s
                WHERE id_ventas=%s
            """, (id_producto, nueva_cantidad, nuevo_precio, self.id_seleccionado))
            conexion.commit()
            self.cargar_datos()
        except Exception as e:
            conexion.rollback()
            self.mostrar_error(f"Error al guardar modificación: {e}")
        finally:
            cursor.close()
            conexion.close()

    # volver al inicio
    def volver_inicio(self, instance):
        self.manager.current = "inicio"

    # si hay un error, aca lo mostramos con un popup
    def mostrar_error(self, mensaje):
        MDDialog(
            text=mensaje,
            buttons=[MDFlatButton(text="Cerrar", on_release=lambda x: self.dialog.dismiss() if hasattr(self, 'dialog') else None)]
        ).open()
