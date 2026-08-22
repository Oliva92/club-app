import streamlit as st
import pandas as pd
import hashlib
import urllib.parse
from datetime import datetime, date

# Configuración Responsive (Celular / PC)
st.set_page_config(page_title="Gestión de Club & Cuotas", page_icon="⚽", layout="wide")

MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
MES_ACTUAL = MESES[datetime.now().month - 1]
ANIO_ACTUAL = datetime.now().year

# --- BASE DE DATOS EN MEMORIA / SESIÓN ---
if "socios_db" not in st.session_state:
    st.session_state.socios_db = pd.DataFrame([
        {
            "id": 1, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Juan Pérez", 
            "dni": "35123456", "telefono": "5491198765432", "apto_medico": "Aprobado", 
            "venc_apto": "2026-12-31", "alergias": "Ninguna", "contacto_emergencia": "1188888888", "estado": "Activo"
        },
        {
            "id": 2, "tipo_registro": "Grupo Familiar", "grupo_familiar": "Familia Gómez", "nombre": "Carlos Gómez", 
            "dni": "30111222", "telefono": "5491112345678", "apto_medico": "Aprobado", 
            "venc_apto": "2026-10-15", "alergias": "Ninguna", "contacto_emergencia": "1122223333", "estado": "Activo"
        },
        {
            "id": 3, "tipo_registro": "Grupo Familiar", "grupo_familiar": "Familia Gómez", "nombre": "Ana Gómez", 
            "dni": "42333444", "telefono": "5491112345678", "apto_medico": "Pendiente", 
            "venc_apto": "2026-05-01", "alergias": "Asma", "contacto_emergencia": "1122223333", "estado": "Activo"
        }
    ])

if "pagos_db" not in st.session_state:
    st.session_state.pagos_db = []

# --- CONTROL DE ACCESO ---
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

# --- MENÚ LATERAL ---
st.sidebar.title("📌 Menú Principal")
opcion = st.sidebar.radio("Ir a:", [
    "📊 Inicio & Control Cuotas", 
    "➕ Registrar Socio / Grupo", 
    "🔍 Padrón de Socios", 
    "💳 Cobrar Cuota"
])

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.auth = False
    st.rerun()

# ------------------------------------------------------------------------------
# 1. DASHBOARD & CONTROL DE CUOTAS
# ------------------------------------------------------------------------------
if opcion == "📊 Inicio & Control Cuotas":
    st.header(f"📊 Resumen y Estado de Cuotas ({MES_ACTUAL} {ANIO_ACTUAL})")
    
    # Cálculos
    df_socios = st.session_state.socios_db.copy()
    
    # Identificar quiénes pagaron el mes actual
    pagos_mes = [p for p in st.session_state.pagos_db if p["mes"] == MES_ACTUAL and p["anio"] == ANIO_ACTUAL]
    
    ids_pagados = []
    for pago in pagos_mes:
        ids_pagados.extend(pago["ids_asociados"])
        
    df_socios["Estado Cuota"] = df_socios["id"].apply(
        lambda x: f"✅ Al día ({MES_ACTUAL})" if x in ids_pagados else f"❌ Adeuda ({MES_ACTUAL})"
    )
    
    total_recaudado = sum([p["monto"] for p in pagos_mes])
    pagados_cnt = len(set(ids_pagados))
    adeudados_cnt = len(df_socios) - pagados_cnt

    col1, col2, col3 = st.columns(3)
    col1.metric("Recaudación Mes Actual", f"$ {total_recaudado:,}")
    col2.metric("Socios Al Día", pagados_cnt)
    col3.metric("Socios Morosos Mes", adeudados_cnt)

    st.markdown("---")
    st.subheader("📋 Detalle de Control por Socio")
    st.dataframe(
        df_socios[["nombre", "tipo_registro", "grupo_familiar", "Estado Cuota", "apto_medico"]],
        use_container_width=True, hide_index=True
    )

# ------------------------------------------------------------------------------
# 2. ALTA DE SOCIO INDIVIDUAL O GRUPO FAMILIAR
# ------------------------------------------------------------------------------
elif opcion == "➕ Registrar Socio / Grupo":
    st.header("Registro de Socios y Ficha Médica")
    
    tipo_reg = st.radio("Tipo de Registro", ["Socio Individual", "Grupo Familiar"], horizontal=True)
    
    with st.form("form_alta"):
        nombre_grupo = "N/A"
        if tipo_reg == "Grupo Familiar":
            nombre_grupo = st.text_input("Nombre del Grupo Familiar (ej: Familia Gómez)").strip()
            
        st.subheader("Datos del Socio")
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre y Apellido Completo")
        dni = c2.text_input("DNI / Cédula")
        tel = st.text_input("Teléfono WhatsApp (ej: 5491112345678)")
        
        st.subheader("Ficha Médica & Emergencias")
        c3, c4 = st.columns(2)
        apto = c3.selectbox("Apto Médico", ["Aprobado", "Pendiente", "Rechazado"])
        venc_apto = c4.date_input("Vencimiento del Apto")
        
        contacto_emerg = st.text_input("Teléfono de Emergencia")
        alergias = st.text_area("Observaciones Médicas / Alergias", value="Ninguna")
        
        guardar = st.form_submit_button("Guardar Socio")
        
        if guardar:
            if nombre and dni:
                nuevo = {
                    "id": len(st.session_state.socios_db) + 1,
                    "tipo_registro": "Grupo Familiar" if tipo_reg == "Grupo Familiar" else "Individual",
                    "grupo_familiar": nombre_grupo if tipo_reg == "Grupo Familiar" else "N/A",
                    "nombre": nombre, "dni": dni, "telefono": tel,
                    "apto_medico": apto, "venc_apto": str(venc_apto),
                    "alergias": alergias, "contacto_emergencia": contacto_emerg,
                    "estado": "Activo"
                }
                st.session_state.socios_db = pd.concat([st.session_state.socios_db, pd.DataFrame([nuevo])], ignore_index=True)
                st.success(f"¡Socio {nombre} registrado correctamente!")
            else:
                st.error("El Nombre y DNI son obligatorios.")

# ------------------------------------------------------------------------------
# 3. PADRÓN DE SOCIOS
# ------------------------------------------------------------------------------
elif opcion == "🔍 Padrón de Socios":
    st.header("Padrón General de Socios")
    st.dataframe(st.session_state.socios_db, use_container_width=True, hide_index=True)

# ------------------------------------------------------------------------------
# 4. COBRO DE CUOTAS POR NOMBRE Y GRUPO FAMILIAR
# ------------------------------------------------------------------------------
elif opcion == "💳 Cobrar Cuota":
    st.header("Registrar Cobro de Cuota")
    
    # Búsqueda por Nombre y Apellido
    lista_nombres = st.session_state.socios_db["nombre"].tolist()
    socio_buscado = st.selectbox("Buscar Socio por Nombre y Apellido", options=[""] + lista_nombres)
    
    if socio_buscado:
        socio_data = st.session_state.socios_db[st.session_state.socios_db["nombre"] == socio_buscado].iloc[0]
        
        is_grupo = socio_data["tipo_registro"] == "Grupo Familiar"
        
        if is_grupo:
            nom_grupo = socio_data["grupo_familiar"]
            integrantes = st.session_state.socios_db[st.session_state.socios_db["grupo_familiar"] == nom_grupo]
            st.info(f"👨‍👩‍👧‍👦 **Cobro a Grupo Familiar:** {nom_grupo}")
            st.write("**Integrantes incluidos en el comprobante:**")
            st.dataframe(integrantes[["nombre", "dni", "apto_medico"]], hide_index=True)
            ids_a_cobrar = integrantes["id"].tolist()
            nombres_comprobante = ", ".join(integrantes["nombre"].tolist())
            monto_defecto = 12000.0
        else:
            st.info(f"👤 **Cobro Individual:** {socio_data['nombre']}")
            ids_a_cobrar = [socio_data["id"]]
            nombres_comprobante = socio_data["nombre"]
            monto_defecto = 6000.0

        c1, c2, c3 = st.columns(3)
        mes_cobro = c1.selectbox("Mes a cobrar", MESES, index=MESES.index(MES_ACTUAL))
        anio_cobro = c2.number_input("Año", value=ANIO_ACTUAL)
        monto = c3.number_input("Monto Total ($)", value=monto_defecto, step=500.0)
        
        medio = st.selectbox("Medio de Pago", ["Efectivo", "Transferencia", "Mercado Pago"])
        
        if st.button("Confirmar Pago y Generar Comprobante"):
            nuevo_pago = {
                "ids_asociados": ids_a_cobrar,
                "pagador": socio_data["nombre"],
                "detalle": nombres_comprobante,
                "mes": mes_cobro,
                "anio": anio_cobro,
                "monto": monto,
                "medio": medio,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.pagos_db.append(nuevo_pago)
            st.success("¡Pago cargado exitosamente!")
            
            # Formato de mensaje para WhatsApp
            if is_grupo:
                txt = f"Hola! Confirmamos el pago del *Grupo {nom_grupo}* ({nombres_comprobante}) correspondiente al mes de *{mes_cobro} {anio_cobro}* por un total de *${monto:,.0f}*. ¡Muchas gracias!"
            else:
                txt = f"Hola {socio_data['nombre']}! Confirmamos tu pago del mes de *{mes_cobro} {anio_cobro}* por un total de *${monto:,.0f}*. ¡Muchas gracias!"
                
            wa_url = f"https://wa.me/{socio_data['telefono']}?text={urllib.parse.quote(txt)}"
            st.markdown(f"[📲 **Enviar Comprobante Unificado por WhatsApp**]({wa_url})")
