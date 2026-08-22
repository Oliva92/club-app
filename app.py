import streamlit as st
import pandas as pd
import hashlib
import urllib.parse
from datetime import datetime

# Configuración Responsive (Celular / PC)
st.set_page_config(page_title="Gestión de Club & Fútbol", page_icon="⚽", layout="wide")

import streamlit.components.v1 as components

# Inyección del Manifiesto PWA para instalación en Android/iOS
pwa_html = """
<link rel="manifest" href="https://raw.githubusercontent.com/Oliva92/club-app/main/manifest.json">
<meta name="theme-color" content="#0e1117">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Club Fútbol">
"""
components.html(pwa_html, height=0)

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
            "id": 2, "tipo_registro": "Grupo Familiar", "grupo_familiar": "Familia López", "nombre": "Mateo López", 
            "dni": "48111222", "categoria_futbol": "8va", "telefono": "5491112345678", 
            "apto_medico": "Aprobado", "venc_apto": "2026-10-15", "alergias": "Ninguna", 
            "contacto_emergencia": "1122223333", "estado": "Activo"
        },
        {
            "id": 3, "tipo_registro": "Grupo Familiar", "grupo_familiar": "Familia López", "nombre": "Thiago López", 
            "dni": "52333444", "categoria_futbol": "6ta", "telefono": "5491112345678", 
            "apto_medico": "Pendiente", "venc_apto": "2026-05-01", "alergias": "Asma", 
            "contacto_emergencia": "1122223333", "estado": "Activo"
        }
    ])

if "pagos_db" not in st.session_state:
    st.session_state.pagos_db = []

# --- CONTROL DE ACCESO Y USUARIOS ---
# Contraseñas cifradas en SHA-256
USERS = {
    "admin": hashlib.sha256("Admin2026!Club#".encode()).hexdigest(),
    "cobranzas": hashlib.sha256("Cobras2026!".encode()).hexdigest()
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
    
    df_socios = st.session_state.socios_db.copy()
    
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
    col2.metric("Chicos / Socios Al Día", pagados_cnt)
    col3.metric("Cuotas Pendientes", adeudados_cnt)

    st.markdown("---")
    st.subheader("⚽ Cantidad de Chicos por Categoría de Fútbol")
    
    cat_counts = df_socios["categoria_futbol"].value_counts().reset_index()
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
            
            guardar = st.form_submit_button("Guardar Jugador")
            
            if guardar:
                if nombre and dni:
                    nuevo = {
                        "id": len(st.session_state.socios_db) + 1,
                        "tipo_registro": "Individual",
                        "grupo_familiar": "N/A",
                        "nombre": nombre, "dni": dni, "categoria_futbol": categoria,
                        "telefono": tel, "apto_medico": apto, "venc_apto": str(venc_apto),
                        "alergias": alergias, "contacto_emergencia": contacto_emerg,
                        "estado": "Activo"
                    }
                    st.session_state.socios_db = pd.concat([st.session_state.socios_db, pd.DataFrame([nuevo])], ignore_index=True)
                    st.success(f"¡{nombre} guardado correctamente en la categoría {categoria}!")
                else:
                    st.error("El Nombre y DNI son obligatorios.")

    else:
        st.subheader("👨‍👩‍👧‍👦 Carga de Grupo Familiar")
        nombre_grupo = st.text_input("Nombre del Grupo Familiar (ej: Familia López)").strip()
        tel_familiar = st.text_input("Teléfono Principal / WhatsApp del Grupo")
        contacto_emerg_fam = st.text_input("Teléfono de Emergencia / Madre / Padre")
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
                venc_i = c5.date_input(f"Vencimiento Apto #{i+1}", key=f"venc_{i}")
                alergia_i = st.text_input(f"Alergias / Med. Especial #{i+1}", value="Ninguna", key=f"alergia_{i}")
                
                integrantes_datos.append({
                    "nombre": nom_i, "dni": dni_i, "categoria": cat_i,
                    "apto": apto_i, "venc": str(venc_i), "alergia": alergia_i
                })
                st.markdown("---")
                
            guardar_grupo = st.form_submit_button("Guardar Todo el Grupo Familiar")
            
            if guardar_grupo:
                if nombre_grupo and all([item["nombre"] and item["dni"] for item in integrantes_datos]):
                    nuevos_registros = []
                    start_id = len(st.session_state.socios_db) + 1
                    
                    for idx, item in enumerate(integrantes_datos):
                        nuevos_registros.append({
                            "id": start_id + idx,
                            "tipo_registro": "Grupo Familiar",
                            "grupo_familiar": nombre_grupo,
                            "nombre": item["nombre"],
                            "dni": item["dni"],
                            "categoria_futbol": item["categoria"],
                            "telefono": tel_familiar,
                            "apto_medico": item["apto"],
                            "venc_apto": item["venc"],
                            "alergias": item["alergia"],
                            "contacto_emergencia": contacto_emerg_fam,
                            "estado": "Activo"
                        })
                    
                    st.session_state.socios_db = pd.concat([st.session_state.socios_db, pd.DataFrame(nuevos_registros)], ignore_index=True)
                    st.success(f"¡{len(nuevos_registros)} integrantes registrados correctamente bajo el grupo '{nombre_grupo}'!")
                else:
                    st.error("Por favor completa el nombre del grupo y el Nombre/DNI de todos los integrantes.")

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
            st.dataframe(integrantes[["nombre", "dni", "categoria_futbol", "apto_medico"]], hide_index=True)
            ids_a_cobrar = integrantes["id"].tolist()
            
            nombres_comprobante = ", ".join([f"{r['nombre']} ({r['categoria_futbol']})" for _, r in integrantes.iterrows()])
            monto_defecto = 12000.0
        else:
            st.info(f"👤 **Cobro Individual:** {socio_data['nombre']} | **Categoría:** {socio_data['categoria_futbol']}")
            ids_a_cobrar = [socio_data["id"]]
            nombres_comprobante = f"{socio_data['nombre']} ({socio_data['categoria_futbol']})"
            monto_defecto = 6000.0

        c1, c2, c3 = st.columns(3)
        mes_cobro = c1.selectbox("Mes a cobrar", MESES, index=MESES.index(MES_ACTUAL))
        anio_cobro = c2.number_input("Año", value=ANIO_ACTUAL)
        monto = c3.number_input("Monto Total ($)", value=monto_defecto, step=500.0)
        
        medio = st.selectbox("Medio de Pago", ["Efectivo", "Transferencia", "Mercado Pago"])
        
        if st.button("Confirmar Pago y Guardar Comprobante"):
            receipt_id = f"REC-{len(st.session_state.pagos_db) + 1001}"
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
                "anio": anio_cobro,
                "monto": monto,
                "medio": medio,
                "fecha": fecha_ahora,
                "usuario_cobro": st.session_state.current_user,
                "telefono": socio_data["telefono"],
                "mensaje_wa": msg_txt
            }
            st.session_state.pagos_db.append(nuevo_pago)
            st.success(f"¡Comprobante #{receipt_id} guardado con éxito en el archivo local!")
            
            wa_url = f"https://wa.me/{socio_data['telefono']}?text={urllib.parse.quote(msg_txt)}"
            st.markdown(f"[📲 **Enviar Comprobante Unificado por WhatsApp**]({wa_url})")

# ------------------------------------------------------------------------------
# 5. HISTORIAL / ARCHIVO LOCAL DE COMPROBANTES
# ------------------------------------------------------------------------------
elif opcion == "📑 Historial de Comprobantes":
    st.header("📑 Archivo Local de Comprobantes Guardados")
    
    if len(st.session_state.pagos_db) == 0:
        st.warning("No hay comprobantes cargados en el sistema aún.")
    else:
        df_pagos = pd.DataFrame(st.session_state.pagos_db)
        
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
        """)
        
        wa_url_reprint = f"https://wa.me/{pago_info['telefono']}?text={urllib.parse.quote(pago_info['mensaje_wa'])}"
        st.markdown(f"[📲 **Reenviar Comprobante por WhatsApp**]({wa_url_reprint})")
        
        wa_url_reprint = f"https://wa.me/{pago_info['telefono']}?text={urllib.parse.quote(pago_info['mensaje_wa'])}"
        st.markdown(f"[📲 **Reenviar Comprobante por WhatsApp**]({wa_url_reprint})")
