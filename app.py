import streamlit as st
import pandas as pd
import hashlib
import urllib.parse
from datetime import datetime

# Configuración Responsive (Celular / PC)
st.set_page_config(page_title="Gestión de Club & Fútbol", page_icon="⚽", layout="wide")

# --- ESCUDO DE FONDO (MARCA DE AGUA) ---
# SVG vectorizado del escudo 'VAL' para asegurar carga local inmediata sin bloqueos de servidor
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

# --- BASE DE DATOS EN MEMORIA / SESIÓN ---
if "socios_db" not in st.session_state:
    socios_data = [
        # --- 6ta Categoría ---
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

        # --- 7ma Categoría ---
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

        # --- 8va Categoría ---
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

        # --- 9na Categoría ---
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

        # --- 5ta Categoría ---
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
        {"id": 108, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Bruno Gomez", "dni": "", "direccion": "", "categoria_futbol": "5ta", "tel_madre": "", "tel_padre": "", "apto_medico": "Pendiente", "alergias": "Ninguna", "estado": "Activo"}
    ]
    st.session_state.socios_db = pd.DataFrame(socios_data)
