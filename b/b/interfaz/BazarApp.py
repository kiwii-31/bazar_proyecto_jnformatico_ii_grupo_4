from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from parte_grafica.ventas_screen import ventasScreen
from parte_grafica.registrar_venta_screen import registrarVenta

class inicio_screen(Screen):
    pass

class stock_screen(Screen):
    pass

class reporte_screen(Screen):
    pass

class BazarApp(MDApp):
    def build(self):
        Builder.load_file("interfaz/parte_logica/BazarApp.kv")
        Builder.load_file("interfaz/parte_logica/ventas_screen.kv")
        Builder.load_file("interfaz/parte_logica/registrar_venta_screen.kv")

        sm = ScreenManager()
        sm.add_widget(inicio_screen(name="inicio"))
        sm.add_widget(stock_screen(name="stock"))
        sm.add_widget(ventasScreen(name="ventas"))
        sm.add_widget(registrarVenta(name="registrar_venta"))
        sm.add_widget(reporte_screen(name="reportes"))
        return sm

if __name__ == "__main__":
    BazarApp().run()
