from kivy.uix.screenmanager import Screen
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from clases.conexion import crear_conexion
from kivy.uix.scrollview import ScrollView
from kivymd.uix.button import MDFlatButton

#creamos la ventana de ventas
class ventasScreen(Screen):
    def on_enter(self):
        #se crea la interfaz como una tablan de excel, para luego cargar los datos que haiga en la bdd o se actualizen al momento de una accion
        self.crear_interfaz()
        self.cargar_datos()
        #este es la manera como se determinara que se borra o modifca
        self.id_seleccionado = None

    def crear_interfaz(self):
        #esto para que no se cree de nuevo y haiga duplicados
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
        #aca se crea la tabla    
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

        self.tabla.bind(on_row_press=self.seleccionar_fila)
#aca se crean los botones  de este modulo
        botones = MDBoxLayout(size_hint=(1, None), height=dp(60), spacing=15)
        botones.add_widget(MDRaisedButton(text="Registrar venta", on_release=lambda x: setattr(self.manager, "current", "registrar_venta")))
        #el popup es algo de kivy que me permite crear un mini formulario por asi decirlo sin otra ventana molesta(usar en otros modulos)
        botones.add_widget(MDRaisedButton(text="Modificar venta", on_release=self.abrir_popup_mod))
        botones.add_widget(MDRaisedButton(text="Eliminar venta", on_release=self.eliminar_venta))
        botones.add_widget(MDRaisedButton(text="Volver al inicio", on_release=self.volver_inicio))

        layout_principal.add_widget(titulo)
        layout_principal.add_widget(self.tabla)
        layout_principal.add_widget(botones)

        self.add_widget(layout_principal)
        self.interfaz_creada = True

    #se caragn los datos para suarse con la bdd(hacerlo simpore asi sabemos si hay error con la bdd)
    def cargar_datos(self):
        conexion = crear_conexion()
        if not conexion:
            print("No se pudo conectar a la base de datos")
            return

#se ejecuta un select from de las 2 tablas necesarias como ventas y detalle de venta
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                select v.id, d.id_product, d.cantidad, d.precio_unitario, v.fecha_venta
                from ventas v
                join detalle_venta d ON v.id = d.id_ventas
                order by v.id desc
            """)
            datos = cursor.fetchall()
            self.tabla.row_data = [(str(row[0]), str(row[1]), str(row[2]), str(row[3]), str(row[4])) for row in datos]

        except Exception as e:
            print("Error al cargar los datos:", e)

        finally:
            cursor.close()
            conexion.close()

    #esta funcion sirve para mostrar por consola(momentaneamente) la venta que se selecciono e indicarte si se logro o no
    def seleccionar_fila(self, instance_table, instance_row):
        try:
            self.id_seleccionado = instance_table.row_data[instance_row.index][0]
            print(f"Venta seleccionada: {self.id_seleccionado}")
        #literalemnte da error porque no seleccionas al id, SI O SI CLICK AL ID
        except Exception as e:
            print("Error al seleccionar la fila:", e)

    #este metodo elimina la vent asegun donde el maouse este posicionado o dado clik, gracias al id_selecionado
    def eliminar_venta(self, instance):
        if not self.id_seleccionado:
            print("No se ha seleccionado nada para eliminar")
            return

        conexion = crear_conexion()
        if not conexion:
            print("No se pudo conectar a la base de datos")
            return

#se ejecuta la consulta de esta manera, para evitar que el codigo se haga mas largo de lo que es, borrando el id de venta
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM detalle_venta WHERE id_ventas=%s", (self.id_seleccionado,))
            cursor.execute("DELETE FROM ventas WHERE id=%s", (self.id_seleccionado,))
            conexion.commit()
            print(f"Venta {self.id_seleccionado} eliminada exitosamente")
            self.cargar_datos()
        except Exception as e:
            print("Error al eliminar la venta:", e)
            conexion.rollback()
        finally:
            cursor.close()
            conexion.close()

    #aca se abre el popup
    def abrir_popup_mod(self, instance):
        if not self.id_seleccionado:
            print("No se ha seleccionado nada para modificar")
            return

        conexion = crear_conexion()
        if not conexion:
            print("No se pudo conectar a la base de datos")
            return

        #esta consulta permite modificar solo ciertos cmpos excepto la fecha de centventa segun el id selecionado
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT d.id_product, d.cantidad, d.precio_unitario
                FROM detalle_venta d
                WHERE d.id_ventas = %s LIMIT 1
            """, (self.id_seleccionado,))
            venta = cursor.fetchone()

            if not venta:
                print("No se encontró el detalle de la venta")
                return

            id_producto, cantidad, precio_unitario = venta

            #aca se crea la prte visual del popup
            contenido = MDBoxLayout(orientation="vertical", spacing=dp(10), padding=dp(15), size_hint_y=None)
            contenido.height = dp(200)

            self.input_producto = MDTextField(text=str(id_producto), hint_text="ID Producto")
            self.input_cantidad = MDTextField(text=str(cantidad), hint_text="Cantidad")
            self.input_precio = MDTextField(text=str(precio_unitario), hint_text="Precio Unitario")

            contenido.add_widget(self.input_producto)
            contenido.add_widget(self.input_cantidad)
            contenido.add_widget(self.input_precio)

            self.dialog = MDDialog(
                type="custom",
                content_cls=contenido,
                buttons=[
                    MDFlatButton(text="cancelar", on_release=lambda x: self.dialog.dismiss()),
                    MDRaisedButton(text="guardar", on_release=self.guardar_modificacion)
                ],
                auto_dismiss=False
            )
            self.dialog.open()

        except Exception as e:
            print("Error al abrir popup de modificación:", e)

        finally:
            cursor.close()
            conexion.close()

    #aca me asugro que se guarden las modificaciones segun lo puesto en cada input
    def guardar_modificacion(self, instance):
        nuevo_producto = self.input_producto.text
        nueva_cantidad = self.input_cantidad.text
        nuevo_precio = self.input_precio.text

        conexion = crear_conexion()
        if not conexion:
            print("No se pudo conectar a la base de datos")
            return

        try:
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE detalle_venta
                SET id_product=%s, cantidad=%s, precio_unitario=%s
                WHERE id_ventas=%s
            """, (nuevo_producto, nueva_cantidad, nuevo_precio, self.id_seleccionado))
            conexion.commit()
            print(f"Venta {self.id_seleccionado} modificada correctamente")
            self.dialog.dismiss()
            self.cargar_datos()

        except Exception as e:
            print("Error al guardar modificación:", e)
            conexion.rollback()

        finally:
            cursor.close()
            conexion.close()

   #se vuerlve al inicio
    def volver_inicio(self, instance):
        self.manager.current = "inicio"
