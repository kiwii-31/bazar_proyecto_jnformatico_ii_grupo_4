from clases.conexion import crear_conexion

class DetalleVenta:
    def __init__(self, id, precio_unitario, id_producto, id_venta, cantidad):
        self.id = id
        self.precio_unitario = precio_unitario
        self.id_producto = id_producto
        self.id_venta = id_venta
        self.cantidad = cantidad

    def registrar_venta(self, id_venta, id_producto):
        conexion = crear_conexion()
        if not conexion:
            print("No se conectó a la base de datos")
            return False
        
        try:
            cursor = conexion.cursor()
            for p in id_producto:
                cursor.execute(
                    """INSERT INTO detalle_venta (id_ventas, id_product, cantidad, precio_unitario)
                       VALUES (%s, %s, %s, %s)""",
                    (id_venta, p["id_product"], p["cantidad"], p["precio_unitario"])
                )
            conexion.commit()
            print(f"Los detalles fueron registrados para la venta {id_venta}")
            return True
        
        except Exception as e:
            print("Error al registrar los detalles dados:", e)
            conexion.rollback()
            return False
        
        finally:
            cursor.close()
            conexion.close()
