import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar las variables desde el archivo .env
load_dotenv()

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")

if not URL or not KEY:
    raise ValueError("Faltan las credenciales de Supabase en el archivo .env")

# Cliente global de la base de datos
supabase: Client = create_client(URL, KEY)
