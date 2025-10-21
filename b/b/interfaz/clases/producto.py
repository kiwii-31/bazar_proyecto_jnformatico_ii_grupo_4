from clases.conexion import conectar

class Producto:
    def __init__(self, id, cod_barra, nombre, precio, cantidad, id_cate):
        self.id = id
        self.cod_barra = cod_barra
        self.nombre = nombre
        self.precio = precio
        self.cantidad = cantidad
        self.id_cate = id_cate

    def guardar(self):
        try:
            conexion = conectar()
            if conexion is None:
                raise Exception("No se pudo conectar con la base de datos.")
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO producto (id, cod_barra, nombre, precio, cantidad, id_cate)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.id, self.cod_barra, self.nombre, self.precio, self.cantidad, self.id_cate))
            conexion.commit()
            print(f"Producto '{self.nombre}' agregado correctamente.")
        except Exception as e:
            print(f"Error al guardar producto: {e}")
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def listar():
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM producto")
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al listar productos: {e}")
            return []
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def actualizar_stock(id_producto, nueva_cantidad):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("UPDATE producto SET cantidad = ? WHERE id = ?", (nueva_cantidad, id_producto))
            conexion.commit()
        except Exception as e:
            print(f"Error al actualizar stock: {e}")
        finally:
            if conexion:
                conexion.close()
