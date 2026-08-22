import streamlit as st
import pandas as pd
import hashlib
import urllib.parse
from datetime import datetime, date

# Configuración de página responsive (Celular / PC)
st.set_page_config(page_title="Gestión Club & Ficha Médica", page_icon="⚽", layout="wide")

# Base de datos local (En memoria / Sesión)
if "socios_db" not in st.session_state:
    st.session_state.socios_db = pd.DataFrame([
        {
            "id": 1, "dni": "35123456", "nombre": "Juan Pérez", "telefono": "5491198765432", 
            "apto_medico": "Aprobado", "venc_apto": "2026-12-31", "grupo_sanguineo": "A+",
            "alergias": "Ninguna", "contacto_emergencia": "1188888888", "estado": "Activo"
        }
    ])

if "pagos_db" not in st.session_state:
    st.session_state.pagos_db = []

# Autenticación Básica
USERS = {"admin": hashlib.sha256("admin123".encode()).hexdigest()}

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔒 Control de Acceso - Club")
    usr = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if usr in USERS and USERS[usr] == hashlib.sha256(pwd.encode()).hexdigest():
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
    st.stop()

# Navegación
st.sidebar.title("📌 Menú Principal")
opcion = st.sidebar.radio("Ir a:", ["📊 Inicio", "➕ Alta / Ficha Médica", "🔍 Padron de Socios", "💳 Cobrar Cuota"])

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.auth = False
    st.rerun()

# ------------------------------------------------------------------------------
# 1. DASHBOARD
# ------------------------------------------------------------------------------
if opcion == "📊 Inicio":
    st.header("Resumen del Club")
    col1, col2, col3 = st.columns(3)
    col1.metric("Socios Totales", len(st.session_state.socios_db))
    col2.metric("Recaudación Mes", f"$ {sum([p['monto'] for p in st.session_state.pagos_db]):,}")
    
    # Alerta de aptos médicos vencidos
    hoy = str(date.today())
    vencidos = st.session_state.socios_db[st.session_state.socios_db["venc_apto"] < hoy]
    col3.metric("Aptos Vencidos", len(vencidos))
    
    if not vencidos.empty:
        st.warning("🚨 **Atención:** Hay socios con la Ficha Médica/Apto Vencido")
        st.dataframe(vencidos[["dni", "nombre", "venc_apto"]], hide_index=True)

# ------------------------------------------------------------------------------
# 2. ALTA DE SOCIO CON FICHA MÉDICA
# ------------------------------------------------------------------------------
elif opcion == "➕ Alta / Ficha Médica":
    st.header("Registro de Socio y Salud")
    
    with st.form("form_alta"):
        st.subheader("Datos Personales")
        c1, c2 = st.columns(2)
        dni = c1.text_input("DNI / Cédula")
        nombre = c2.text_input("Nombre Completo")
        tel = c1.text_input("Teléfono (con código de área, ej: 54911...)")
        
        st.subheader("Ficha Médica & Emergencias")
        c3, c4 = st.columns(2)
        apto = c3.selectbox("Estado del Apto Médico", ["Aprobado", "Pendiente", "Rechazado"])
        venc_apto = c4.date_input("Fecha de Vencimiento del Apto")
        
        c5, c6 = st.columns(2)
        sangre = c5.selectbox("Grupo Sanguíneo", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Desconocido"])
        contacto_emerg = c6.text_input("Teléfono de Emergencia / Familiar")
        alergias = st.text_area("Alergias, Enfermedades Crónicas o Observaciones Médicas", value="Ninguna")
        
        guardar = st.form_submit_button("Guardar Socio")
        
        if guardar:
            if dni and nombre:
                nuevo_socio = {
                    "id": len(st.session_state.socios_db) + 1,
                    "dni": dni, "nombre": nombre, "telefono": tel,
                    "apto_medico": apto, "venc_apto": str(venc_apto),
                    "grupo_sanguineo": sangre, "alergias": alergias,
                    "contacto_emergencia": contacto_emerg, "estado": "Activo"
                }
                st.session_state.socios_db = pd.concat([st.session_state.socios_db, pd.DataFrame([nuevo_socio])], ignore_index=True)
                st.success(f"¡Socio {nombre} registrado exitosamente!")
            else:
                st.error("DNI y Nombre son obligatorios.")

# ------------------------------------------------------------------------------
# 3. PADRÓN DE SOCIOS
# ------------------------------------------------------------------------------
elif opcion == "🔍 Padron de Socios":
    st.header("Padrón General de Socios")
    st.dataframe(st.session_state.socios_db, use_container_width=True, hide_index=True)

# ------------------------------------------------------------------------------
# 4. COBRO DE CUOTAS Y WHATSAPP
# ------------------------------------------------------------------------------
elif opcion == "💳 Cobrar Cuota":
    st.header("Registrar Cobro")
    dni_buscar = st.text_input("Ingresar DNI del Socio")
    
    socio_filtrado = st.session_state.socios_db[st.session_state.socios_db["dni"] == dni_buscar]
    
    if not socio_filtrado.empty:
        socio = socio_filtrado.iloc[0]
        st.info(f"Socio: **{socio['nombre']}** | Estado Apto Médico: **{socio['apto_medico']}** (Vence: {socio['venc_apto']})")
        
        if socio["apto_medico"] != "Aprobado":
            st.error("⚠️ Advertencia: Este socio NO tiene el apto médico aprobado.")
            
        c1, c2 = st.columns(2)
        mes = c1.selectbox("Mes a cobrar", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
        monto = c2.number_input("Monto ($)", value=5000, step=500)
        medio = st.selectbox("Medio de Pago", ["Efectivo", "Transferencia", "Mercado Pago"])
        
        if st.button("Confirmar y Generar Recibo"):
            st.session_state.pagos_db.append({"dni": socio["dni"], "monto": monto, "mes": mes})
            st.success("Pago guardado correctamente.")
            
            # Enlace de WhatsApp
            texto = f"Hola {socio['nombre']}, recibimos tu pago de la cuota de {mes} por ${monto}. ¡Muchas gracias!"
            link_wa = f"https://wa.me/{socio['telefono']}?text={urllib.parse.quote(texto)}"
            st.markdown(f"[📲 **Enviar Comprobante por WhatsApp**]({link_wa})")