import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()  # Cargar variables de entorno desde .env

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "clave_secreta_segura")


# Configuración de conexión a la base de datos
DB_CONFIG = {
    "dbname": "cultivared",
    "user": "postgres",
    "password": "1234",
    "host": "34.45.183.188",
    "port": "5432"   
}

# Función para obtener conexión
def get_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print("Error de conexión:", e)
        return None

# Probar conexión
conn = get_connection()
if conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print("Conectado a:", db_version)
    conn.close()