# algo a destacar, es que el conector habitual me daba error con la version de python, por eso 
#use otra libreria, que si me dejo
import pymysql

def crear_conexion():
    try:
        conexion = pymysql.connect(
            host="127.0.0.1",
            user="root",
            password="ezequiel",
            database="bazar",
            port=2026,
            connect_timeout=5
        )
        print("conexión establecida con la base de datos")
        return conexion
    except pymysql.MySQLError as e:
        print("error al conectar con la base de datos:", e)
        return None
