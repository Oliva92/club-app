import streamlit as st
import pandas as pd
import hashlib
import urllib.parse
from datetime import datetime
from conexion import supabase
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import streamlit as st

def generar_pdf_comprobante(datos_cobro):
    """
    Genera un recibo en PDF en memoria (BytesIO) usando ReportLab.
    """
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Encabezado
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, f"COMPROBANTE DE PAGO - RECIBO #{datos_cobro.get('receipt_id')}")
    
    # Detalle del Cobro
    p.setFont("Helvetica", 12)
    p.drawString(100, 710, f"Fecha: {datos_cobro.get('fecha')}")
    p.drawString(100, 690, f"Pagador / Socio: {datos_cobro.get('pagador')}")
    p.drawString(100, 670, f"Detalle: {datos_cobro.get('detalle')}")
    p.drawString(100, 650, f"Período: {datos_cobro.get('mes')}/{datos_cobro.get('anio')}")
    p.drawString(100, 630, f"Medio de Pago: {datos_cobro.get('medio')}")
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 600, f"Monto Total: ${datos_cobro.get('monto')}")
    
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(100, 560, f"Atendido por: {datos_cobro.get('usuario_cobro')}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer.getvalue()

def subir_pdf_supabase(bytes_pdf, nombre_archivo):
    path_en_bucket = f"recibos/{nombre_archivo}"
    
    # Se agrega 'upsert': 'true' para reescribir si el archivo ya existe
    res = supabase.storage.from_("comprobantes").upload(
        path=path_en_bucket,
        file=bytes_pdf,
        file_options={
            "content-type": "application/pdf",
            "upsert": "true"
        }
    )
    
    url_publica = supabase.storage.from_("comprobantes").get_public_url(path_en_bucket)
    return url_publica
    # 1. Armar el diccionario con los datos del cobro



# Configuración Responsive (Celular / PC)
st.set_page_config(page_title="Gestión de Club & Fútbol", page_icon="⚽", layout="wide")

# --- ESCUDO DE FONDO (MARCA DE AGUA) ---
ESCUDO_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="100%" height="100%">
  <path d="M 250 40 L 420 80 C 420 280 350 380 250 460 C 150 380 80 280 80 80 Z" fill="#E65100" stroke="#FFFFFF" stroke-width="12"/>
  <path d="M 250 20 L 440 65 C 440 290 365 400 250 485 C 135 400 60 290 60 65 Z" fill="none" stroke="#4A0000" stroke-width="8"/>
  <text x="250" y="270" font-family="Georgia, serif" font-size="120" font-weight="bold" fill="#000000" text-anchor="middle">VAL</text>
</svg>
"""

import base64
b64_svg = base64.b64encode(ESCUDO_SVG.encode('utf-8')).decode('utf-8')

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(14, 17, 23, 0.88), rgba(14, 17, 23, 0.88)), url("data:image/svg+xml;base64,{b64_svg}");
        background-attachment: fixed;
        background-size: 450px;
        background-repeat: no-repeat;
        background-position: center;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
MES_ACTUAL = MESES[datetime.now().month - 1]
ANIO_ACTUAL = datetime.now().year

CATEGORIAS_FUTBOL = ["Ninguna / Adulto", "9na", "8va", "7ma", "6ta", "5ta", "Sub-12", "Sub-14", "Sub-21"]

# --- FUNCIONES DE INTERACCIÓN CON SUPABASE ---

def obtener_todos_los_socios():
    res = supabase.table("socios").select("*").execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

def guardar_socio(datos):
    datos_para_insertar = datos.copy()
    datos_para_insertar.pop("id", None)
    
    try:
        res = supabase.table("socios").insert(datos_para_insertar).execute()
        return res
    except Exception as e:
        # Esto imprimirá el error real de Postgres en la pantalla de Streamlit
        st.error(f"Error al guardar socio '{datos_para_insertar.get('nombre')}': {e}")
        raise e

def actualizar_socio(socio_id, datos):
    res = supabase.table("socios").update(datos).eq("id", socio_id).execute()
    return res.data

def registrar_cobro(datos_cobro):
    res = supabase.table("cobranzas").insert(datos_cobro).execute()
    return res.data

def obtener_todos_los_cobros():
    res = supabase.table("cobranzas").select("*").order("fecha", desc=True).execute()
    return res.data

# --- MIGRACIÓN INICIAL A SUPABASE ---
SOCIOS_INICIALES = [
    # 6ta Categoría
    {"id": 1, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Valentin Brinso", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "2226542073", "tel_padre": "2271432530", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 2, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Joaquin Campos", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "2271436860", "tel_padre": "1124055037", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 3, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Dylan Cinalli", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "2226511049", "tel_padre": "2226547080", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 4, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Alvaro Diaz", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "1153313470", "tel_padre": "2226459518", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 5, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Lisandro Dutrey", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "2226514387", "tel_padre": "2226536715", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 6, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Ciro Echegaray", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "2226517001", "tel_padre": "2226448501", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 7, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Lionel Franco", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "2226533605", "tel_padre": "2226477628", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 8, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Mateo Grignoli", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "2226508115", "tel_padre": "2226625073", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 9, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Nicolás Guayan", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "2271418936", "tel_padre": "2226474453", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 10, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Mirko Guntin", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "1132324131", "tel_padre": "2226518116", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 11, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Dylan Halvide", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "2226684951", "tel_padre": "2226600372", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 12, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Benjamin Lemos", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "1171435844", "tel_padre": "1157746529", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 13, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Santiago Mega", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "2226689137", "tel_padre": "22266002278", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 14, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Ludovico Miranda", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "2226554206", "tel_padre": "2226598540", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 15, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Dylan Morales", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "2271414348", "tel_padre": "2271410512", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 16, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Dylan Ojeda", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "2226542300", "tel_padre": "2226478570", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 17, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Esteban Panizza", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "2226681638", "tel_padre": "2226681361", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 18, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Juan Pereira", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "2226482512", "tel_padre": "2226516368", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 19, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Maximo Silva", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "2226460398", "tel_padre": "2271493084", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 20, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Joaquin Snidersich", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "2227574991", "tel_padre": "2226620954", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 21, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Ian Soto", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "1165105095", "tel_padre": "1141641952", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 22, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Brandon Tabares", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "2226547929", "tel_padre": "2226540123", "apto_medico": "Pendiente", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 23, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Juan Taricco", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "2226532535", "tel_padre": "2226471459", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 24, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Ramon Taricco", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "", "tel_padre": "", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 25, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Enzo Torres", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "2226525463", "tel_padre": "2271410027", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 26, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Santino Torres", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "2226479552", "tel_padre": "2226483865", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 27, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Benjamin Zabala", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "", "tel_padre": "", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 28, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Francisco Zamora", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "2226444753", "tel_padre": "2226538966", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 29, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Bruno Burosso", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "", "tel_padre": "", "apto_medico": "Pendiente", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 30, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Valentino Fucillo", "dni": "", "direccion": "", "categoria_futbol": "6ta", "tel_madre": "", "tel_padre": "", "apto_medico": "Pendiente", "alergias": "Ninguna", "estado": "Activo"},
    # 7ma Categoría
    {"id": 31, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Damian Acuña", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "1149383937", "tel_padre": "2226473714", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 32, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Francisco Agüero", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "2226514595", "tel_padre": "2226490744", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 33, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Lionel Aguilera", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "2226549760", "tel_padre": "2226544866", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 34, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Erik Albornoz", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "2226539611", "tel_padre": "2226457765", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 35, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Tiziano Avila", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "2226529143", "tel_padre": "2226626961", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 36, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Santino Burgos", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "", "tel_padre": "", "apto_medico": "Pendiente", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 37, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Ian Carugati", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "2226448933", "tel_padre": "2226448937", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 38, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Pedro Diaz", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "1153313470", "tel_padre": "2226459518", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 39, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Uriel Diaz", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "2226517790", "tel_padre": "2226598987", "apto_medico": "Pendiente", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 40, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Alex Gelvez", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "2271434952", "tel_padre": "2271433937", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 41, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Kevin Gonzalez", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "", "tel_padre": "", "apto_medico": "Pendiente", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 42, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Franco Grignoli", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "2226476656", "tel_padre": "2226475288", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 43, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Martin Laborda", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "2227506069", "tel_padre": "2226482673", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 44, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Bruno Leiva", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "2226458652", "tel_padre": "2226471757", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 45, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Neymar Lopez", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "", "tel_padre": "", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 46, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Ciro Maderna", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "2226567274", "tel_padre": "2226475931", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 47, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Mirko Morfese", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "2226688577", "tel_padre": "2271417980", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 48, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Mateo Muñoz", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "", "tel_padre": "", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 49, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Benjamin Oliva", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "2226511439", "tel_padre": "2226546784", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 50, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Ian Ortiz", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "2226626895", "tel_padre": "2271413165", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 51, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Lorenzo Rolon", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "2226475931", "tel_padre": "2226556784", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 52, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Hugo Rosas", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "2271411049", "tel_padre": "2271436286", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 53, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Gonzalo Sanchez", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "", "tel_padre": "", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 54, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Lisandro Suarez", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "2226474313", "tel_padre": "2226444205", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 55, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Tiziano Torres", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "2226479552", "tel_padre": "2226483865", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 56, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Tiziano Urbizu", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "2226530087", "tel_padre": "2226556112", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 57, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Dylan Urbizu", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "2226530087", "tel_padre": "2226556112", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 58, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Uriel Urdin", "dni": "", "direccion": "", "categoria_futbol": "7ma", "tel_madre": "", "tel_padre": "", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    # 8va Categoría
    {"id": 59, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Stefano Devincenzi", "dni": "", "direccion": "", "categoria_futbol": "8va", "tel_madre": "2226502466", "tel_padre": "2226487042", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 60, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Alexander Diarte", "dni": "", "direccion": "", "categoria_futbol": "8va", "tel_madre": "2226621404", "tel_padre": "2226683597", "apto_medico": "Pendiente", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 61, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Ramiro Donoso", "dni": "", "direccion": "", "categoria_futbol": "8va", "tel_madre": "1123899653", "tel_padre": "1123898400", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 62, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Uriel Espindola", "dni": "", "direccion": "", "categoria_futbol": "8va", "tel_madre": "2271436999", "tel_padre": "2226511313", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 63, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Noah Gigena", "dni": "", "direccion": "", "categoria_futbol": "8va", "tel_madre": "2226508654", "tel_padre": "2271431275", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 64, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Lorenzo Gimenez", "dni": "", "direccion": "", "categoria_futbol": "8va", "tel_madre": "1158007500", "tel_padre": "1158007007", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 65, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Josue Gomez", "dni": "", "direccion": "", "categoria_futbol": "8va", "tel_madre": "2226447087", "tel_padre": "2226446287", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 66, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Lorenzo Lagarde", "dni": "", "direccion": "", "categoria_futbol": "8va", "tel_madre": "2271410872", "tel_padre": "2271430022", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 67, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Enrique Maccio", "dni": "", "direccion": "", "categoria_futbol": "8va", "tel_madre": "2226481091", "tel_padre": "2226448869", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 68, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Maximo Medina", "dni": "", "direccion": "", "categoria_futbol": "8va", "tel_madre": "2271411761", "tel_padre": "2271416762", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 69, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Enzo Moyano", "dni": "", "direccion": "", "categoria_futbol": "8va", "tel_madre": "2226554196", "tel_padre": "2223524827", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 70, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Leonardo Ortega", "dni": "", "direccion": "", "categoria_futbol": "8va", "tel_madre": "2226533108", "tel_padre": "2226506640", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 71, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Vicente Priore", "dni": "", "direccion": "", "categoria_futbol": "8va", "tel_madre": "2271433828", "tel_padre": "2271435026", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 72, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Gino Risso", "dni": "", "direccion": "", "categoria_futbol": "8va", "tel_madre": "2226490952", "tel_padre": "1126746476", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 73, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Jesuan Rivas", "dni": "", "direccion": "", "categoria_futbol": "8va", "tel_madre": "2226623931", "tel_padre": "2271410310", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 74, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Nicolas Rojas", "dni": "", "direccion": "", "categoria_futbol": "8va", "tel_madre": "2226553422", "tel_padre": "2226607692", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 75, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Jonas Rolon", "dni": "", "direccion": "", "categoria_futbol": "8va", "tel_madre": "2226446777", "tel_padre": "2271433931", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 76, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Joaquin Romano", "dni": "", "direccion": "", "categoria_futbol": "8va", "tel_madre": "2226460372", "tel_padre": "2226477749", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 77, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Izan Romano", "dni": "", "direccion": "", "categoria_futbol": "8va", "tel_madre": "2226620680", "tel_padre": "2226688839", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 78, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Maximo Vilca", "dni": "", "direccion": "", "categoria_futbol": "8va", "tel_madre": "2226516829", "tel_padre": "2271419387", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    # 9na Categoría
    {"id": 79, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Josias Astargo", "dni": "", "direccion": "", "categoria_futbol": "9na", "tel_madre": "", "tel_padre": "", "apto_medico": "Pendiente", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 80, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Federico Caccialanza", "dni": "", "direccion": "", "categoria_futbol": "9na", "tel_madre": "", "tel_padre": "", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 81, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Jeremias Carugati", "dni": "", "direccion": "", "categoria_futbol": "9na", "tel_madre": "", "tel_padre": "", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 82, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Kayla Castro", "dni": "", "direccion": "", "categoria_futbol": "9na", "tel_madre": "", "tel_padre": "", "apto_medico": "Pendiente", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 83, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Malaika Castro", "dni": "", "direccion": "", "categoria_futbol": "9na", "tel_madre": "", "tel_padre": "", "apto_medico": "Pendiente", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 84, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Mateo Cinalli", "dni": "", "direccion": "", "categoria_futbol": "9na", "tel_madre": "2226511049", "tel_padre": "2226547080", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 85, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Dilan Diaz", "dni": "", "direccion": "", "categoria_futbol": "9na", "tel_madre": "2226517790", "tel_padre": "2226598987", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 86, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Benicio Encabo", "dni": "", "direccion": "", "categoria_futbol": "9na", "tel_madre": "", "tel_padre": "", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 87, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Alfonso Espindola", "dni": "", "direccion": "", "categoria_futbol": "9na", "tel_madre": "", "tel_padre": "", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 88, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Axel Laborda", "dni": "", "direccion": "", "categoria_futbol": "9na", "tel_madre": "2227506069", "tel_padre": "2226482673", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 89, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Zenon Loyola", "dni": "", "direccion": "", "categoria_futbol": "9na", "tel_madre": "", "tel_padre": "", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 90, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Aaron Luna", "dni": "", "direccion": "", "categoria_futbol": "9na", "tel_madre": "2276445802", "tel_padre": "", "apto_medico": "Pendiente", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 91, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Juan Martínez", "dni": "", "direccion": "", "categoria_futbol": "9na", "tel_madre": "", "tel_padre": "", "apto_medico": "Pendiente", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 92, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Bianca Muñoz", "dni": "", "direccion": "", "categoria_futbol": "9na", "tel_madre": "2226604456", "tel_padre": "2271413951", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 93, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Elian Reyna", "dni": "", "direccion": "", "categoria_futbol": "9na", "tel_madre": "2271470623", "tel_padre": "2271411593", "apto_medico": "Pendiente", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 94, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Mateo Sola", "dni": "", "direccion": "", "categoria_futbol": "9na", "tel_madre": "2226567274", "tel_padre": "2226475931", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 95, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Jona Troussel", "dni": "", "direccion": "", "categoria_futbol": "9na", "tel_madre": "", "tel_padre": "", "apto_medico": "Pendiente", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 96, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Lorenzo Zagari", "dni": "", "direccion": "", "categoria_futbol": "9na", "tel_madre": "2227445010", "tel_padre": "2271469245", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    # 5ta Categoría
    {"id": 97, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Benjamin Agüero", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "2226444509", "tel_padre": "2226449800", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 98, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Joaquin Andrade", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "", "tel_padre": "", "apto_medico": "Pendiente", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 99, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Tomas Benitez", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "1123360415", "tel_padre": "2271418803", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 100, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Tiziano Campos", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "2271436860", "tel_padre": "1124055037", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 101, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Benjamin Casao", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "2226475453", "tel_padre": "2226448043", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 102, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Ian Challen", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "2226445729", "tel_padre": "", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 103, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Thomas Cordoba", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "2271415773", "tel_padre": "2271415531", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 104, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Jhonatan Coronel", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "2226514387", "tel_padre": "2226536715", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 105, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Thiago Fazio", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "2226539639", "tel_padre": "2226540812", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 106, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Renzo Fernandez", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "2271416417", "tel_padre": "2271411067", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 107, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Fabricio Flores", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "2226509390", "tel_padre": "2226445199", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 108, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Bruno Gomez", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "2226447087", "tel_padre": "2226446287", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 109, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Ignacio Kiryliuk", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "1154588281", "tel_padre": "2226596092", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 110, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Matias Lias", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "2271417431", "tel_padre": "2226602288", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 111, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Ezequiel Moyano", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "2271413448", "tel_padre": "2227403197", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 112, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Dylan Nievas", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "2271416886", "tel_padre": "2271418962", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 113, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Piero Palavecino", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "2226532851", "tel_padre": "2226458105", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 114, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Francisco Peñaloza", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "2271486241", "tel_padre": "222624806", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 115, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Samuel Perez", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "", "tel_padre": "", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 116, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Thiago Pintos", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "2226569312", "tel_padre": "2271418930", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 117, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Bastian Saldaña", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "2226480632", "tel_padre": "2226519385", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 118, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Ezequiel Tabares", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "2226547119", "tel_padre": "222627614", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 119, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Nahuel Tuama", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "2226506315", "tel_padre": "2226487778", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 120, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Enzo Urdin", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "", "tel_padre": "", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 121, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Teo Zonfrillo", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "2226524401", "tel_padre": "2226624960", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    # Sub-14 Categoría
    {"id": 122, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Yanela Alfonso", "dni": "", "direccion": "", "categoria_futbol": "Sub-14", "tel_madre": "", "tel_padre": "", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 123, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Maira Altamirano", "dni": "", "direccion": "", "categoria_futbol": "Sub-14", "tel_madre": "2226685096", "tel_padre": "1132064418", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 124, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Martina Aranda", "dni": "", "direccion": "", "categoria_futbol": "Sub-14", "tel_madre": "2226555465", "tel_padre": "2226685517", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 125, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Ainara Carro", "dni": "", "direccion": "", "categoria_futbol": "Sub-14", "tel_madre": "", "tel_padre": "", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 126, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Antonella Granara", "dni": "", "direccion": "", "categoria_futbol": "Sub-14", "tel_madre": "2226447840", "tel_padre": "2226546013", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 127, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Mia Halvide", "dni": "", "direccion": "", "categoria_futbol": "Sub-14", "tel_madre": "2226547146", "tel_padre": "2226459895", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 128, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Maia Lastra", "dni": "", "direccion": "", "categoria_futbol": "Sub-14", "tel_madre": "", "tel_padre": "", "apto_medico": "Pendiente", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 129, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Sara Leonard", "dni": "", "direccion": "", "categoria_futbol": "Sub-14", "tel_madre": "", "tel_padre": "", "apto_medico": "Pendiente", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 130, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Juana Machado", "dni": "", "direccion": "", "categoria_futbol": "Sub-14", "tel_madre": "2226517661", "tel_padre": "2226686928", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 131, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Brunella Moreno", "dni": "", "direccion": "", "categoria_futbol": "Sub-14", "tel_madre": "2226599130", "tel_padre": "2226446287", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 132, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Natasha Ruizdia", "dni": "", "direccion": "", "categoria_futbol": "Sub-14", "tel_madre": "2226502019", "tel_padre": "2226502413", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    # Sub-21 Categoría
    {"id": 133, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Yumila Altamirano", "dni": "", "direccion": "", "categoria_futbol": "Sub-21", "tel_madre": "2226622810", "tel_padre": "2226476922", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 134, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Lucila Berguñan", "dni": "", "direccion": "", "categoria_futbol": "Sub-21", "tel_madre": "2271416350", "tel_padre": "2226476359", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 135, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Tatiana Diaz", "dni": "", "direccion": "", "categoria_futbol": "Sub-21", "tel_madre": "2226557472", "tel_padre": "2226457324", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 136, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Sofia Diaz", "dni": "", "direccion": "", "categoria_futbol": "Sub-21", "tel_madre": "2226557472", "tel_padre": "2226457324", "apto_medico": "Pendiente", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 137, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Rocio Gomez", "dni": "", "direccion": "", "categoria_futbol": "Sub-21", "tel_madre": "", "tel_padre": "", "apto_medico": "Pendiente", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 138, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Naiara Guayan", "dni": "", "direccion": "", "categoria_futbol": "Sub-21", "tel_madre": "2226476438", "tel_padre": "2226529076", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 139, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Priscila Jurao", "dni": "", "direccion": "", "categoria_futbol": "Sub-21", "tel_madre": "2226474313", "tel_padre": "2224528145", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 140, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Jazmin Lara", "dni": "", "direccion": "", "categoria_futbol": "Sub-21", "tel_madre": "2271410482", "tel_padre": "2226554772", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 141, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Xiomara Moreno", "dni": "", "direccion": "", "categoria_futbol": "Sub-21", "tel_madre": "2226447087", "tel_padre": "2226446287", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 142, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Marina Mujica", "dni": "", "direccion": "", "categoria_futbol": "Sub-21", "tel_madre": "", "tel_padre": "", "apto_medico": "Pendiente", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 143, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Micaela Muñoz", "dni": "", "direccion": "", "categoria_futbol": "Sub-21", "tel_madre": "", "tel_padre": "", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 144, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Valentina Peralta", "dni": "", "direccion": "", "categoria_futbol": "Sub-21", "tel_madre": "", "tel_padre": "", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 145, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Selene Rodriguez", "dni": "", "direccion": "", "categoria_futbol": "Sub-21", "tel_madre": "2226684483", "tel_padre": "2226483520", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 146, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Quimey Rolon", "dni": "", "direccion": "", "categoria_futbol": "Sub-21", "tel_madre": "2226517661", "tel_padre": "2226686928", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 147, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Ramona Rolon", "dni": "", "direccion": "", "categoria_futbol": "Sub-21", "tel_madre": "", "tel_padre": "", "apto_medico": "Pendiente", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 148, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Jade Sola", "dni": "", "direccion": "", "categoria_futbol": "Sub-21", "tel_madre": "2226567274", "tel_padre": "2226475931", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 149, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Albertina Tarazona", "dni": "", "direccion": "", "categoria_futbol": "Sub-21", "tel_madre": "2271438912", "tel_padre": "2226607870", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 150, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Gisele Tarazona", "dni": "", "direccion": "", "categoria_futbol": "Sub-21", "tel_madre": "", "tel_padre": "", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 151, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Andrea Torres", "dni": "", "direccion": "", "categoria_futbol": "Sub-21", "tel_madre": "", "tel_padre": "", "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 152, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Perla", "dni": "", "direccion": "", "categoria_futbol": "Sub-21", "tel_madre": "", "tel_padre": "", "apto_medico": "Pendiente", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 153, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Brisa", "dni": "", "direccion": "", "categoria_futbol": "Sub-21", "tel_madre": "", "tel_padre": "", "apto_medico": "Pendiente", "alergias": "Ninguna", "estado": "Activo"},
    {"id": 154, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Camila", "dni": "", "direccion": "", "categoria_futbol": "Sub-21", "tel_madre": "", "tel_padre": "", "apto_medico": "Pendiente", "alergias": "Ninguna", "estado": "Activo"}
]

# Carga inicial y obtención de datos desde Supabase
st.session_state.socios_db = obtener_todos_los_socios()

if st.session_state.socios_db.empty:
    for s in SOCIOS_INICIALES:
        guardar_socio(s)
    st.session_state.socios_db = obtener_todos_los_socios()

# Agrupación automática de familias
def _telefonos_familiares(registro):
    return {
        str(registro[campo]).strip()
        for campo in ("tel_madre", "tel_padre")
        if campo in registro and str(registro[campo]).strip()
    }

def _detectar_grupos_familiares(df):
    grupos_por_telefono = {}
    for idx, registro in df.iterrows():
        for telefono in _telefonos_familiares(registro):
            grupos_por_telefono.setdefault(telefono, set()).add(idx)

    pendientes = [indices for indices in grupos_por_telefono.values() if len(indices) > 1]
    componentes = []
    while pendientes:
        componente = set(pendientes.pop())
        cambio = True
        while cambio:
            cambio = False
            for grupo in pendientes[:]:
                if componente & grupo:
                    componente |= grupo
                    pendientes.remove(grupo)
                    cambio = True
        componentes.append(componente)
    return componentes

if "familias_detectadas" not in st.session_state and not st.session_state.socios_db.empty:
    st.session_state.familias_detectadas = _detectar_grupos_familiares(st.session_state.socios_db)
    for numero, integrantes in enumerate(st.session_state.familias_detectadas, start=1):
        nombre_grupo = f"Familia detectada {numero}"
        for idx in integrantes:
            socio_id = int(st.session_state.socios_db.loc[idx, "id"])
            datos_upd = {"tipo_registro": "Grupo Familiar", "grupo_familiar": nombre_grupo}
            actualizar_socio(socio_id, datos_upd)
    st.session_state.socios_db = obtener_todos_los_socios()

# --- CONTROL DE ACCESO Y USUARIOS ---
USERS = {
    "admin": hashlib.sha256("Club2026#".encode()).hexdigest(),
    "cobranzas": hashlib.sha256("Cobro2026!".encode()).hexdigest()
}

if "auth" not in st.session_state:
    st.session_state.auth = False
    st.session_state.current_user = ""

if not st.session_state.auth:
    st.title("🔒 Control de Acceso - Club")
    usr = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if usr in USERS and USERS[usr] == hashlib.sha256(pwd.encode()).hexdigest():
            st.session_state.auth = True
            st.session_state.current_user = usr
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
    st.stop()

# --- MENÚ LATERAL ---
st.sidebar.title(f"👤 Usuario: {st.session_state.current_user}")
opcion = st.sidebar.radio("Ir a:", [
    "📊 Inicio & Categorías", 
    "➕ Registrar Socio / Grupo",
    "✏️ Editar / Dar de Baja Socio",
    "🔍 Padrón & Listas", 
    "💳 Cobrar Cuota",
    "📑 Historial de Comprobantes"
])

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.auth = False
    st.session_state.current_user = ""
    st.rerun()

# ------------------------------------------------------------------------------
# 1. DASHBOARD & CONTROL POR CATEGORÍA
# ------------------------------------------------------------------------------
if opcion == "📊 Inicio & Categorías":
    st.header(f"📊 Control General y Cuotas ({MES_ACTUAL} {ANIO_ACTUAL})")
    
    df_activos = st.session_state.socios_db[st.session_state.socios_db["estado"] == "Activo"].copy()
    
    cobros_todos = obtener_todos_los_cobros()
    pagos_mes = [p for p in cobros_todos if p.get("mes") == MES_ACTUAL and p.get("anio") == ANIO_ACTUAL]
    
    ids_pagados = []
    for pago in pagos_mes:
        if pago.get("ids_asociados"):
            ids_pagados.extend(pago["ids_asociados"])
        
    df_activos["Estado Cuota"] = df_activos["id"].apply(
        lambda x: f"✅ Al día ({MES_ACTUAL})" if x in ids_pagados else f"❌ Adeuda ({MES_ACTUAL})"
    )
    
    total_recaudado = sum([p.get("monto", 0) for p in pagos_mes])
    pagados_cnt = len(set(ids_pagados))
    adeudados_cnt = len(df_activos) - pagados_cnt

    col1, col2, col3 = st.columns(3)
    col1.metric("Recaudación Mes Actual", f"$ {total_recaudado:,}")
    col2.metric("Chicos / Socios Al Día", pagados_cnt)
    col3.metric("Cuotas Pendientes", adeudados_cnt)

    st.markdown("---")
    st.subheader("⚽ Cantidad de Chicos Activos por Categoría")
    
    cat_counts = df_activos["categoria_futbol"].value_counts().reset_index()
    cat_counts.columns = ["Categoría", "Cantidad de Chicos"]
    st.dataframe(cat_counts, use_container_width=True, hide_index=True)

# ------------------------------------------------------------------------------
# 2. ALTA DE JUGADOR INDIVIDUAL O GRUPO FAMILIAR
# ------------------------------------------------------------------------------
elif opcion == "➕ Registrar Socio / Grupo":
    st.header("Registro de Chicos / Socios y Ficha Médica")
    
    tipo_reg = st.radio("Tipo de Registro", ["Socio / Jugador Individual", "Grupo Familiar"], horizontal=True)
    
    if tipo_reg == "Socio / Jugador Individual":
        with st.form("form_alta_individual"):
            st.subheader("Datos Personales")
            c1, c2 = st.columns(2)
            nombre = c1.text_input("Nombre y Apellido Completo")
            dni = c2.text_input("DNI / Cédula")
            
            c3, c4 = st.columns(2)
            direccion = c3.text_input("Dirección / Domicilio")
            categoria = c4.selectbox("Categoría de Fútbol", CATEGORIAS_FUTBOL)
            
            st.subheader("Teléfonos de Contacto")
            t1, t2 = st.columns(2)
            tel_madre = t1.text_input("Teléfono Madre / WhatsApp (ej: 5491112345678)")
            tel_padre = t2.text_input("Teléfono Padre / WhatsApp (ej: 5491112345678)")
            
            st.subheader("Ficha Médica")
            apto = st.selectbox("Apto Médico", ["Aprobado", "Pendiente", "Rechazado"])
            alergias = st.text_area("Observaciones Médicas / Alergias", value="Ninguna")
            
            guardar = st.form_submit_button("Guardar Jugador")
            
            if guardar:
                if nombre and dni:
                    nuevo = {
                        "tipo_registro": "Individual",
                        "grupo_familiar": "N/A",
                        "nombre": nombre, "dni": dni, "direccion": direccion,
                        "categoria_futbol": categoria,
                        "tel_madre": tel_madre, "tel_padre": tel_padre,
                        "apto_medico": apto, "alergias": alergias,
                        "estado": "Activo"
                    }
                    guardar_socio(nuevo)
                    st.session_state.socios_db = obtener_todos_los_socios()
                    st.success(f"¡{nombre} guardado correctamente en Supabase en la categoría {categoria}!")
                else:
                    st.error("El Nombre y DNI son obligatorios.")

    else:
        st.subheader("👨‍👩‍👧‍👦 Carga de Grupo Familiar")
        nombre_grupo = st.text_input("Nombre del Grupo Familiar (ej: Familia López)").strip()
        direccion_fam = st.text_input("Dirección del Grupo Familiar")
        
        c_t1, c_t2 = st.columns(2)
        tel_madre_fam = c_t1.text_input("Teléfono Madre / WhatsApp del Grupo")
        tel_padre_fam = c_t2.text_input("Teléfono Padre / WhatsApp del Grupo")
        
        cant_chicos = st.number_input("¿Cuántos niños/integrantes forman este Grupo Familiar?", min_value=1, max_value=6, value=2, step=1)
        
        st.markdown("---")
        
        with st.form("form_alta_grupo"):
            integrantes_datos = []
            
            for i in range(int(cant_chicos)):
                st.markdown(f"#### 👦 Integrante #{i+1}")
                c1, c2, c3 = st.columns(3)
                nom_i = c1.text_input(f"Nombre Completo #{i+1}", key=f"nom_{i}")
                dni_i = c2.text_input(f"DNI #{i+1}", key=f"dni_{i}")
                cat_i = c3.selectbox(f"Categoría #{i+1}", CATEGORIAS_FUTBOL, key=f"cat_{i}")
                
                c4, c5 = st.columns(2)
                apto_i = c4.selectbox(f"Apto Médico #{i+1}", ["Aprobado", "Pendiente", "Rechazado"], key=f"apto_{i}")
                alergia_i = c5.text_input(f"Alergias / Med. Especial #{i+1}", value="Ninguna", key=f"alergia_{i}")
                
                integrantes_datos.append({
                    "nombre": nom_i, "dni": dni_i, "categoria": cat_i,
                    "apto": apto_i, "alergia": alergia_i
                })
                st.markdown("---")
                
            guardar_grupo = st.form_submit_button("Guardar Todo el Grupo Familiar")
            
            if guardar_grupo:
                if nombre_grupo and all([item["nombre"] and item["dni"] for item in integrantes_datos]):
                    for item in integrantes_datos:
                        nuevo_reg = {
                            "tipo_registro": "Grupo Familiar",
                            "grupo_familiar": nombre_grupo,
                            "nombre": item["nombre"],
                            "dni": item["dni"],
                            "direccion": direccion_fam,
                            "categoria_futbol": item["categoria"],
                            "tel_madre": tel_madre_fam,
                            "tel_padre": tel_padre_fam,
                            "apto_medico": item["apto"],
                            "alergias": item["alergia"],
                            "estado": "Activo"
                        }
                        guardar_socio(nuevo_reg)
                    
                    st.session_state.socios_db = obtener_todos_los_socios()
                    st.success(f"¡Integrantes registrados correctamente bajo el grupo '{nombre_grupo}' en Supabase!")
                else:
                    st.error("Por favor completa el nombre del grupo y el Nombre/DNI de todos los integrantes.")

# ------------------------------------------------------------------------------
# 3. EDITAR / DAR DE BAJA SOCIO
# ------------------------------------------------------------------------------
elif opcion == "✏️ Editar / Dar de Baja Socio":
    st.header("✏️ Modificar Ficha o Dar de Baja un Socio")
    
    lista_socios = st.session_state.socios_db["nombre"].tolist() if not st.session_state.socios_db.empty else []
    socio_sel = st.selectbox("Seleccionar Socio a Modificar:", options=[""] + lista_socios)
    
    if socio_sel:
        socio_data = st.session_state.socios_db[st.session_state.socios_db["nombre"] == socio_sel].iloc[0]
        socio_id = int(socio_data["id"])
        
        with st.form("form_editar_socio"):
            st.subheader(f"Editando la Ficha de: {socio_data['nombre']}")
            
            c1, c2, c3 = st.columns(3)
            nuevo_nombre = c1.text_input("Nombre y Apellido", value=socio_data["nombre"])
            nuevo_dni = c2.text_input("DNI", value=socio_data["dni"])
            nuevo_estado = c3.selectbox("Estado del Socio", ["Activo", "Inactivo / Dado de Baja"], index=0 if socio_data["estado"] == "Activo" else 1)
            
            c4, c5 = st.columns(2)
            nueva_direccion = c4.text_input("Dirección", value=socio_data["direccion"])
            nueva_cat = c5.selectbox("Categoría de Fútbol", CATEGORIAS_FUTBOL, index=CATEGORIAS_FUTBOL.index(socio_data["categoria_futbol"]) if socio_data["categoria_futbol"] in CATEGORIAS_FUTBOL else 0)
            
            st.subheader("Contacto Parentales")
            t1, t2 = st.columns(2)
            nuevo_tel_madre = t1.text_input("Teléfono Madre", value=socio_data["tel_madre"])
            nuevo_tel_padre = t2.text_input("Teléfono Padre", value=socio_data["tel_padre"])
            
            st.subheader("Ficha Médica")
            apto_opts = ["Aprobado", "Pendiente", "Rechazado"]
            nuevo_apto = st.selectbox("Apto Médico", apto_opts, index=apto_opts.index(socio_data["apto_medico"]) if socio_data["apto_medico"] in apto_opts else 0)
            nuevas_alergias = st.text_area("Alergias / Med. Especial", value=socio_data["alergias"])
            
            btn_actualizar = st.form_submit_button("Guardar Cambios")
            
            if btn_actualizar:
                payload = {
                    "nombre": nuevo_nombre,
                    "dni": nuevo_dni,
                    "estado": nuevo_estado,
                    "direccion": nueva_direccion,
                    "categoria_futbol": nueva_cat,
                    "tel_madre": nuevo_tel_madre,
                    "tel_padre": nuevo_tel_padre,
                    "apto_medico": nuevo_apto,
                    "alergias": nuevas_alergias
                }
                actualizar_socio(socio_id, payload)
                st.session_state.socios_db = obtener_todos_los_socios()
                st.success(f"¡Ficha de {nuevo_nombre} actualizada con éxito en Supabase!")

# ------------------------------------------------------------------------------
# 4. PADRÓN & LISTAS POR CATEGORÍA
# ------------------------------------------------------------------------------
elif opcion == "🔍 Padrón & Listas":
    st.header("Padrón General y Filtro por Categoría")
    
    col_f1, col_f2 = st.columns(2)
    filtro_cat = col_f1.selectbox("Filtrar por Categoría de Fútbol:", ["Todas"] + CATEGORIAS_FUTBOL)
    filtro_est = col_f2.selectbox("Estado del Socio:", ["Solo Activos", "Dado de Baja / Inactivos", "Todos"])
    
    df_ver = st.session_state.socios_db.copy()
    
    if not df_ver.empty:
        if filtro_cat != "Todas":
            df_ver = df_ver[df_ver["categoria_futbol"] == filtro_cat]
            
        if filtro_est == "Solo Activos":
            df_ver = df_ver[df_ver["estado"] == "Activo"]
        elif filtro_est == "Dado de Baja / Inactivos":
            df_ver = df_ver[df_ver["estado"] != "Activo"]
            
        st.subheader(f"Listado ({len(df_ver)} registros)")
        st.dataframe(
            df_ver[["nombre", "dni", "estado", "direccion", "categoria_futbol", "tipo_registro", "grupo_familiar", "apto_medico", "tel_madre", "tel_padre"]],
            use_container_width=True, hide_index=True
        )

# ------------------------------------------------------------------------------
# 5. COBRO DE CUOTAS POR NOMBRE Y GRUPO FAMILIAR
# ------------------------------------------------------------------------------
elif opcion == "💳 Cobrar Cuota":
    st.header("Registrar Cobro de Cuota")
    
    df_activos = st.session_state.socios_db[st.session_state.socios_db["estado"] == "Activo"] if not st.session_state.socios_db.empty else pd.DataFrame()
    lista_nombres = df_activos["nombre"].tolist() if not df_activos.empty else []
    socio_buscado = st.selectbox("Buscar por Nombre y Apellido (Solo Activos)", options=[""] + lista_nombres)
    
    if socio_buscado:
        socio_data = df_activos[df_activos["nombre"] == socio_buscado].iloc[0]
        
        is_grupo = socio_data["tipo_registro"] == "Grupo Familiar"
        
        if is_grupo:
            nom_grupo = socio_data["grupo_familiar"]
            integrantes = df_activos[df_activos["grupo_familiar"] == nom_grupo]
            st.info(f"👨‍👩‍👧‍👦 **Cobro a Grupo Familiar:** {nom_grupo}")
            st.write("**Integrantes e información del grupo:**")
            st.dataframe(integrantes[["nombre", "dni", "categoria_futbol", "apto_medico"]], hide_index=True)
            ids_a_cobrar = [int(i) for i in integrantes["id"].tolist()]
            
            nombres_comprobante = ", ".join([f"{r['nombre']} ({r['categoria_futbol']})" for _, r in integrantes.iterrows()])
            monto_defecto = 12000.0
        else:
            st.info(f"👤 **Cobro Individual:** {socio_data['nombre']} | **Categoría:** {socio_data['categoria_futbol']}")
            ids_a_cobrar = [int(socio_data["id"])]
            nombres_comprobante = f"{socio_data['nombre']} ({socio_data['categoria_futbol']})"
            monto_defecto = 6000.0

        c1, c2, c3 = st.columns(3)
        mes_cobro = c1.selectbox("Mes a cobrar", MESES, index=MESES.index(MES_ACTUAL))
        anio_cobro = c2.number_input("Año", value=ANIO_ACTUAL)
        monto = c3.number_input("Monto Total ($)", value=monto_defecto, step=500.0)
        
        medio = st.selectbox("Medio de Pago", ["Efectivo", "Transferencia", "Mercado Pago"])
        
        st.subheader("📲 Envío de Comprobante")
        destino_wa = st.radio("¿A qué teléfono enviar el recibo?", [
            f"Madre ({socio_data['tel_madre']})", 
            f"Padre ({socio_data['tel_padre']})",
            "Otro número"
        ])
        
        if "Madre" in destino_wa:
            tel_envio = socio_data['tel_madre']
        elif "Padre" in destino_wa:
            tel_envio = socio_data['tel_padre']
        else:
            tel_envio = st.text_input("Ingresar otro teléfono con código de área (ej: 5491112345678)")
        
        if st.button("Confirmar Pago y Guardar Comprobante"):
            cobros_existentes = obtener_todos_los_cobros()
            receipt_id = f"REC-{len(cobros_existentes) + 1001}"
            fecha_ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if is_grupo:
                msg_txt = f"Hola! Confirmamos el pago del *Grupo {nom_grupo}* [{nombres_comprobante}] correspondiente a la cuota de *{mes_cobro} {anio_cobro}* por un total de *${monto:,.0f}*. Comprobante #{receipt_id}. ¡Muchas gracias!"
            else:
                msg_txt = f"Hola {socio_data['nombre']}! Confirmamos tu pago de la cuota de *{mes_cobro} {anio_cobro}* ({socio_data['categoria_futbol']}) por un total de *${monto:,.0f}*. Comprobante #{receipt_id}. ¡Muchas gracias!"

            nuevo_pago = {
                "receipt_id": receipt_id,
                "ids_asociados": ids_a_cobrar,
                "pagador": socio_data["nombre"],
                "detalle": nombres_comprobante,
                "mes": mes_cobro,
                "anio": int(anio_cobro),
                "monto": float(monto),
                "medio": medio,
                "fecha": fecha_ahora,
                "usuario_cobro": st.session_state.current_user,
                "telefono": tel_envio,
                "mensaje_wa": msg_txt
            }
            registrar_cobro(nuevo_pago)
            st.success(f"¡Comprobante #{receipt_id} guardado con éxito en Supabase!")
            
            if tel_envio:
                wa_url = f"https://wa.me/{tel_envio}?text={urllib.parse.quote(msg_txt)}"
                st.markdown(f"[📲 **Enviar Comprobante Unificado por WhatsApp**]({wa_url})")
                # 1. Asegurar que solo se muestre si el usuario está autenticado
if st.session_state.get("autenticado", False):

    # 2. Formulario de Cobranza
    with st.form("form_registro_cobro"):
        st.subheader("Registrar Cobro")
        
        pagador = st.text_input("Pagador")
        monto = st.number_input("Monto", min_value=0.0)
        
        # El botón de envío
        submit_button = st.form_submit_button("Guardar Cobro")

    # 3. La lógica de guardado Y los mensajes SOLO se ejecutan si se presionó el botón
    if submit_button:
        nuevo_cobro = {
            "receipt_id": f"REC-{uuid.uuid4().hex[:6].upper()}",
            "pagador": pagador,
            "monto": monto,
            # ... resto de tus campos ...
        }
        
        # Generar y subir PDF
        pdf_bytes = generar_pdf_comprobante(nuevo_cobro)
        nombre_archivo = f"recibo_{nuevo_cobro['receipt_id']}.pdf"
        url_pdf = subir_pdf_supabase(pdf_bytes, nombre_archivo)
        
        nuevo_cobro["url_pdf"] = url_pdf
        supabase.table("cobranzas").insert(nuevo_cobro).execute()
        
        # El cartel informativo ahora solo saldrá UNA VEZ al hacer clic
        st.success("¡Cobro registrado y PDF guardado correctamente!")
        st.download_button("📄 Descargar PDF", data=pdf_bytes, file_name=nombre_archivo, mime="application/pdf")

else:
    # Pantalla de Login si no está autenticado
    st.title("Iniciar Sesión")
    # ... formulario de login ...

# ------------------------------------------------------------------------------
# 6. HISTORIAL / COMPROBANTES EN SUPABASE
# ------------------------------------------------------------------------------
    if opcion == "📑 Historial de Comprobantes":
    st.header("📑 Archivo de Comprobantes en la Nube")
    
    cobros_list = obtener_todos_los_cobros()
    
    if len(cobros_list) == 0:
        st.warning("No hay comprobantes cargados en el sistema aún.")
    else:
        df_pagos = pd.DataFrame(cobros_list)
        
        st.subheader("Búsqueda y Registros Guardados")
        st.dataframe(
            df_pagos[["receipt_id", "fecha", "pagador", "detalle", "mes", "anio", "monto", "medio", "usuario_cobro"]],
            use_container_width=True, hide_index=True
        )
        
        st.markdown("---")
        st.subheader("🔍 Consultar y Reimprimir Comprobante")
        
        receipt_sel = st.selectbox("Seleccionar Comprobante por N°", df_pagos["receipt_id"].tolist())
        pago_info = df_pagos[df_pagos["receipt_id"] == receipt_sel].iloc[0]
        
        st.markdown(f"""
        > **N° Comprobante:** {pago_info['receipt_id']}  
        > **Fecha/Hora:** {pago_info['fecha']}  
        > **Cobrado por:** {pago_info['usuario_cobro']}  
        > **Detalle Chicos/Socios:** {pago_info['detalle']}  
        > **Período:** {pago_info['mes']} {pago_info['anio']}  
        > **Monto:** ${pago_info['monto']:,.2f} ({pago_info['medio']})  
        > **Teléfono Notificado:** {pago_info['telefono']}  
        """)
        
        if pago_info['telefono']:
            wa_url_reprint = f"https://wa.me/{pago_info['telefono']}?text={urllib.parse.quote(pago_info['mensaje_wa'])}"
            st.markdown(f"[📲 **Reenviar Comprobante por WhatsApp**]({wa_url_reprint})")
          
