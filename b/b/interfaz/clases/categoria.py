from clases.conexion import conectar

class Categoria:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre

    def guardar(self):
        try:
            conexion = conectar()
            if conexion is None:
                raise Exception("No se pudo conectar con la base de datos.")
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO categoria (id, nombre) VALUES (?, ?)", (self.id, self.nombre))
            conexion.commit()
            print(f" Categoría '{self.nombre}' agregada correctamente.")
        except Exception as e:
            print(f" Error al guardar categoría: {e}")
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def listar():
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM categoria")
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al listar categorías: {e}")
            return []
        finally:
            if conexion:
                conexion.close()
