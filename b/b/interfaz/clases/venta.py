from clases.conexion import crear_conexion

class Venta:
    def __init__(self, id=None, fecha_venta=None):
        self.id = id
        self.fecha_venta = fecha_venta

    def registrar(self):
        conexion = crear_conexion()
        if not conexion:
            return None

        try:
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO ventas (fecha_venta) VALUES (NOW())")
            conexion.commit()

            self.id = cursor.lastrowid
            print(f"Venta creada con el ID: {self.id}")
            return self.id

        except Exception as e:
            print(f"Error al registrar la venta: {e}")
            conexion.rollback()
            return None

        finally:
            cursor.close()
            conexion.close()



