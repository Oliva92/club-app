import streamlit as st
import pandas as pd
import hashlib
import urllib.parse
from datetime import datetime

# Configuración Responsive (Celular / PC)
st.set_page_config(page_title="Gestión de Club & Fútbol", page_icon="⚽", layout="wide")

MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
MES_ACTUAL = MESES[datetime.now().month - 1]
ANIO_ACTUAL = datetime.now().year

CATEGORIAS_FUTBOL = ["Ninguna / Adulto", "9na", "8va", "7ma", "6ta", "5ta", "Sub-12", "Sub-14", "Sub-21"]

# --- BASE DE DATOS EN MEMORIA / SESIÓN ---
if "socios_db" not in st.session_state:
    st.session_state.socios_db = pd.DataFrame([
        {
            "id": 1, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Juan Pérez", 
            "dni": "50123456", "categoria_futbol": "9na", "telefono": "5491198765432", 
            "apto_medico": "Aprobado", "venc_apto": "2026-12-31", "alergias": "Ninguna", 
            "contacto_emergencia": "1188888888", "estado": "Activo"
        },
        {
            "id": 2, "tipo_registro": "Grupo Familiar", "grupo_familiar": "Familia Gómez", "nombre": "Carlos Gómez", 
            "dni": "48111222", "categoria_futbol": "Sub-14", "telefono": "5491112345678", 
            "apto_medico": "Aprobado", "venc_apto": "2026-10-15", "alergias": "Ninguna", 
            "contacto_emergencia": "1122223333", "estado": "Activo"
        },
        {
            "id": 3, "tipo_registro": "Grupo Familiar", "grupo_familiar": "Familia Gómez", "nombre": "Ana Gómez", 
            "dni": "52333444", "categoria_futbol": "Sub-12", "telefono": "5491112345678", 
            "apto_medico": "Pendiente", "venc_apto": "2026-05-01", "alergias": "Asma", 
            "contacto_emergencia": "1122223333", "estado": "Activo"
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
    "📊 Inicio & Categorías", 
    "➕ Registrar Jugador / Grupo", 
    "🔍 Padrón & Listas", 
    "💳 Cobrar Cuota"
])

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.auth = False
    st.rerun()

# ------------------------------------------------------------------------------
# 1. DASHBOARD & CONTROL POR CATEGORÍA
# ------------------------------------------------------------------------------
if opcion == "📊 Inicio & Categorías":
    st.header(f"📊 Control General y Cuotas ({MES_ACTUAL} {ANIO_ACTUAL})")
    
    df_socios = st.session_state.socios_db.copy()
    
    # Identificar pagos del mes corriente
    pagos_mes = [p for p in st.session_state.pagos_db if p["mes"] == MES_ACTUAL and p["anio"] == ANIO_ACTUAL]
    ids_pagados = []
    for pago in pagos_mes:
        ids_pagados.extend(pago["ids_asociados"])
        
    df_socios["Estado Cuota"] = df_socios["id"].apply(
        lambda x: f"✅ Al día ({MES_ACTUAL})" if x in ids_pagados else f"❌ Adeuda ({MES_ACTUAL})"
    )
    
    # Métricas Principales
    total_recaudado = sum([p["monto"] for p in pagos_mes])
    pagados_cnt = len(set(ids_pagados))
    adeudados_cnt = len(df_socios) - pagados_cnt

    col1, col2, col3 = st.columns(3)
    col1.metric("Recaudación Mes Actual", f"$ {total_recaudado:,}")
    col2.metric("Chicos / Socios Al Día", pagados_cnt)
    col3.metric("Cuotas Pendientes", adeudados_cnt)

    st.markdown("---")
    st.subheader("⚽ Cantidad de Chicos por Categoría de Fútbol")
    
    # Resumen por Categoría
    cat_counts = df_socios["categoria_futbol"].value_counts().reset_index()
    cat_counts.columns = ["Categoría", "Cantidad de Chicos"]
    st.dataframe(cat_counts, use_container_width=True, hide_index=True)

# ------------------------------------------------------------------------------
# 2. ALTA DE JUGADOR / GRUPO CON CATEGORÍA
# ------------------------------------------------------------------------------
elif opcion == "➕ Registrar Jugador / Grupo":
    st.header("Registro de Chicos / Socios y Ficha Médica")
    
    tipo_reg = st.radio("Tipo de Registro", ["Socio / Jugador Individual", "Grupo Familiar"], horizontal=True)
    
    with st.form("form_alta"):
        nombre_grupo = "N/A"
        if tipo_reg == "Grupo Familiar":
            nombre_grupo = st.text_input("Nombre del Grupo Familiar (ej: Familia Gómez)").strip()
            
        st.subheader("Datos del Jugador / Socio")
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre y Apellido Completo")
        dni = c2.text_input("DNI / Cédula")
        
        c3, c4 = st.columns(2)
        categoria = c3.selectbox("Categoría de Fútbol", CATEGORIAS_FUTBOL)
        tel = c4.text_input("Teléfono WhatsApp (ej: 5491112345678)")
        
        st.subheader("Ficha Médica & Emergencias")
        c5, c6 = st.columns(2)
        apto = c5.selectbox("Apto Médico", ["Aprobado", "Pendiente", "Rechazado"])
        venc_apto = c6.date_input("Vencimiento del Apto Médico")
        
        contacto_emerg = st.text_input("Teléfono de Emergencia / Madre / Padre")
        alergias = st.text_area("Observaciones Médicas / Alergias", value="Ninguna")
        
        guardar = st.form_submit_button("Guardar Jugador / Socio")
        
        if guardar:
            if nombre and dni:
                nuevo = {
                    "id": len(st.session_state.socios_db) + 1,
                    "tipo_registro": "Grupo Familiar" if tipo_reg == "Grupo Familiar" else "Individual",
                    "grupo_familiar": nombre_grupo if tipo_reg == "Grupo Familiar" else "N/A",
                    "nombre": nombre, "dni": dni, "categoria_futbol": categoria,
                    "telefono": tel, "apto_medico": apto, "venc_apto": str(venc_apto),
                    "alergias": alergias, "contacto_emergencia": contacto_emerg,
                    "estado": "Activo"
                }
                st.session_state.socios_db = pd.concat([st.session_state.socios_db, pd.DataFrame([nuevo])], ignore_index=True)
                st.success(f"¡{nombre} guardado correctamente en la categoría {categoria}!")
            else:
                st.error("El Nombre y DNI son obligatorios.")

# ------------------------------------------------------------------------------
# 3. PADRÓN & LISTAS POR CATEGORÍA
# ------------------------------------------------------------------------------
elif opcion == "🔍 Padrón & Listas":
    st.header("Padrón General y Filtro por Categoría")
    
    filtro_cat = st.selectbox("Filtrar por Categoría de Fútbol:", ["Todas"] + CATEGORIAS_FUTBOL)
    
    df_ver = st.session_state.socios_db.copy()
    if filtro_cat != "Todas":
        df_ver = df_ver[df_ver["categoria_futbol"] == filtro_cat]
        
    st.subheader(f"Listado ({len(df_ver)} registros)")
    st.dataframe(
        df_ver[["nombre", "dni", "categoria_futbol", "tipo_registro", "grupo_familiar", "apto_medico", "telefono", "contacto_emergencia"]],
        use_container_width=True, hide_index=True
    )

# ------------------------------------------------------------------------------
# 4. COBRO DE CUOTAS POR NOMBRE Y GRUPO FAMILIAR
# ------------------------------------------------------------------------------
elif opcion == "💳 Cobrar Cuota":
    st.header("Registrar Cobro de Cuota")
    
    # Búsqueda por Nombre y Apellido
    lista_nombres = st.session_state.socios_db["nombre"].tolist()
    socio_buscado = st.selectbox("Buscar por Nombre y Apellido", options=[""] + lista_nombres)
    
    if socio_buscado:
        socio_data = st.session_state.socios_db[st.session_state.socios_db["nombre"] == socio_buscado].iloc[0]
        
        is_grupo = socio_data["tipo_registro"] == "Grupo Familiar"
        
        if is_grupo:
            nom_grupo = socio_data["grupo_familiar"]
            integrantes = st.session_state.socios_db[st.session_state.socios_db["grupo_familiar"] == nom_grupo]
            st.info(f"👨‍👩‍👧‍👦 **Cobro a Grupo Familiar:** {nom_grupo}")
            st.write("**Integrantes e información del grupo:**")
            st.dataframe(integrantes[["nombre", "categoria_futbol", "apto_medico"]], hide_index=True)
            ids_a_cobrar = integrantes["id"].tolist()
            nombres_comprobante = ", ".join(integrantes["nombre"].tolist())
            monto_defecto = 12000.0
        else:
            st.info(f"👤 **Cobro Individual:** {socio_data['nombre']} | **Categoría:** {socio_data['categoria_futbol']}")
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
                txt = f"Hola! Confirmamos el pago del *Grupo {nom_grupo}* ({nombres_comprobante}) correspondiente a la cuota de *{mes_cobro} {anio_cobro}* por un total de *${monto:,.0f}*. ¡Muchas gracias!"
            else:
                txt = f"Hola {socio_data['nombre']}! Confirmamos tu pago de la cuota de *{mes_cobro} {anio_cobro}* ({socio_data['categoria_futbol']}) por un total de *${monto:,.0f}*. ¡Muchas gracias!"
                
            wa_url = f"https://wa.me/{socio_data['telefono']}?text={urllib.parse.quote(txt)}"
            st.markdown(f"[📲 **Enviar Comprobante Unificado por WhatsApp**]({wa_url})")
