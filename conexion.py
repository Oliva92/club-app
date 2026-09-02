import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

# Carga variables de un archivo .env si existe (entorno local)
load_dotenv()

# Prioriza st.secrets (Streamlit Cloud) y si no, usa os.getenv (Local)
url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
key = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Faltan las credenciales de Supabase en Secrets o .env")

supabase: Client = create_client(url, key)
