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
    st.session_state.socios_db = pd.DataFrame([
        {
            "id": 1, "tipo_registro": "Individual", "grupo_familiar": "N/A", "nombre": "Juan Pérez", 
            "dni": "50123456", "direccion": "Av. San Martín 123", "categoria_futbol": "9na", 
            "tel_madre": "5491198765432", "tel_padre": "5491187654321", 
            "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"
        },
        {
            "id": 2, "tipo_registro": "Grupo Familiar", "grupo_familiar": "Familia López", "nombre": "Mateo López", 
            "dni": "48111222", "direccion": "Calle Mitre 456", "categoria_futbol": "8va", 
            "tel_madre": "5491112345678", "tel_padre": "5491122334455", 
            "apto_medico": "Aprobado", "alergias": "Ninguna", "estado": "Activo"
        },
        {
            "id": 3, "tipo_registro": "Grupo Familiar", "grupo_familiar": "Familia López", "nombre": "Thiago López", 
            "dni": "52333444", "direccion": "Calle Mitre 456", "categoria_futbol": "6ta", 
            "tel_madre": "5491112345678", "tel_padre": "5491122334455", 
            "apto_medico": "Pendiente", "alergias": "Asma", "estado": "Activo"
        }
    ])

if "pagos_db" not in st.session_state:
    st.session_state.pagos_db = []

# --- CONTROL DE ACCESO Y USUARIOS ---
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
    
    pagos_mes = [p for p in st.session_state.pagos_db if p["mes"] == MES_ACTUAL and p["anio"] == ANIO_ACTUAL]
    ids_pagados = []
    for pago in pagos_mes:
        ids_pagados.extend(pago["ids_asociados"])
        
    df_activos["Estado Cuota"] = df_activos["id"].apply(
        lambda x: f"✅ Al día ({MES_ACTUAL})" if x in ids_pagados else f"❌ Adeuda ({MES_ACTUAL})"
    )
    
    total_recaudado = sum([p["monto"] for p in pagos_mes])
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
                        "id": len(st.session_state.socios_db) + 1,
                        "tipo_registro": "Individual",
                        "grupo_familiar": "N/A",
                        "nombre": nombre, "dni": dni, "direccion": direccion,
                        "categoria_futbol": categoria,
                        "tel_madre": tel_madre, "tel_padre": tel_padre,
                        "apto_medico": apto, "alergias": alergias,
                        "estado": "Activo"
                    }
                    st.session_state.socios_db = pd.concat([st.session_state.socios_db, pd.DataFrame([nuevo])], ignore_index=True)
                    st.success(f"¡{nombre} guardado correctamente en la categoría {categoria}!")
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
                    nuevos_registros = []
                    start_id = len(st.session_state.socios_db) + 1
                    
                    for idx, item in enumerate(integrantes_datos):
                        nuevos_registros.append({
                            "id": start_id + idx,
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
                        })
                    
                    st.session_state.socios_db = pd.concat([st.session_state.socios_db, pd.DataFrame(nuevos_registros)], ignore_index=True)
                    st.success(f"¡{len(nuevos_registros)} integrantes registrados correctamente bajo el grupo '{nombre_grupo}'!")
                else:
                    st.error("Por favor completa el nombre del grupo y el Nombre/DNI de todos los integrantes.")

# ------------------------------------------------------------------------------
# 3. EDITAR / DAR DE BAJA SOCIO
# ------------------------------------------------------------------------------
elif opcion == "✏️ Editar / Dar de Baja Socio":
    st.header("✏️ Modificar Ficha o Dar de Baja un Socio")
    
    lista_socios = st.session_state.socios_db["nombre"].tolist()
    socio_sel = st.selectbox("Seleccionar Socio a Modificar:", options=[""] + lista_socios)
    
    if socio_sel:
        idx = st.session_state.socios_db[st.session_state.socios_db["nombre"] == socio_sel].index[0]
        socio_data = st.session_state.socios_db.loc[idx]
        
        with st.form("form_editar_socio"):
            st.subheader(f"Editando la Ficha de: {socio_data['nombre']}")
            
            c1, c2, c3 = st.columns(3)
            nuevo_nombre = c1.text_input("Nombre y Apellido", value=socio_data["nombre"])
            nuevo_dni = c2.text_input("DNI", value=socio_data["dni"])
            nuevo_estado = c3.selectbox("Estado del Socio", ["Activo", "Inactivo / Dado de Baja"], index=0 if socio_data["estado"] == "Activo" else 1)
            
            c4, c5 = st.columns(2)
            nueva_direccion = c4.text_input("Dirección", value=socio_data["direccion"])
            nueva_cat = c5.selectbox("Categoría de Fútbol", CATEGORIAS_FUTBOL, index=CATEGORIAS_FUTBOL.index(socio_data["categoria_futbol"]))
            
            st.subheader("Contacto Parentales")
            t1, t2 = st.columns(2)
            nuevo_tel_madre = t1.text_input("Teléfono Madre", value=socio_data["tel_madre"])
            nuevo_tel_padre = t2.text_input("Teléfono Padre", value=socio_data["tel_padre"])
            
            st.subheader("Ficha Médica")
            apto_opts = ["Aprobado", "Pendiente", "Rechazado"]
            nuevo_apto = st.selectbox("Apto Médico", apto_opts, index=apto_opts.index(socio_data["apto_medico"]))
            nuevas_alergias = st.text_area("Alergias / Med. Especial", value=socio_data["alergias"])
            
            btn_actualizar = st.form_submit_button("Guardar Cambios")
            
            if btn_actualizar:
                st.session_state.socios_db.loc[idx, "nombre"] = nuevo_nombre
                st.session_state.socios_db.loc[idx, "dni"] = nuevo_dni
                st.session_state.socios_db.loc[idx, "estado"] = nuevo_estado
                st.session_state.socios_db.loc[idx, "direccion"] = nueva_direccion
                st.session_state.socios_db.loc[idx, "categoria_futbol"] = nueva_cat
                st.session_state.socios_db.loc[idx, "tel_madre"] = nuevo_tel_madre
                st.session_state.socios_db.loc[idx, "tel_padre"] = nuevo_tel_padre
                st.session_state.socios_db.loc[idx, "apto_medico"] = nuevo_apto
                st.session_state.socios_db.loc[idx, "alergias"] = nuevas_alergias
                
                st.success(f"¡Ficha de {nuevo_nombre} actualizada con éxito!")

# ------------------------------------------------------------------------------
# 4. PADRÓN & LISTAS POR CATEGORÍA
# ------------------------------------------------------------------------------
elif opcion == "🔍 Padrón & Listas":
    st.header("Padrón General y Filtro por Categoría")
    
    col_f1, col_f2 = st.columns(2)
    filtro_cat = col_f1.selectbox("Filtrar por Categoría de Fútbol:", ["Todas"] + CATEGORIAS_FUTBOL)
    filtro_est = col_f2.selectbox("Estado del Socio:", ["Solo Activos", "Dado de Baja / Inactivos", "Todos"])
    
    df_ver = st.session_state.socios_db.copy()
    
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
    
    df_activos = st.session_state.socios_db[st.session_state.socios_db["estado"] == "Activo"]
    lista_nombres = df_activos["nombre"].tolist()
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
                "telefono": tel_envio,
                "mensaje_wa": msg_txt
            }
            st.session_state.pagos_db.append(nuevo_pago)
            st.success(f"¡Comprobante #{receipt_id} guardado con éxito en el archivo local!")
            
            if tel_envio:
                wa_url = f"https://wa.me/{tel_envio}?text={urllib.parse.quote(msg_txt)}"
                st.markdown(f"[📲 **Enviar Comprobante Unificado por WhatsApp**]({wa_url})")

# ------------------------------------------------------------------------------
# 6. HISTORIAL / ARCHIVO LOCAL DE COMPROBANTES
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
        > **Teléfono Notificado:** {pago_info['telefono']}  
        """)
        
        if pago_info['telefono']:
            wa_url_reprint = f"https://wa.me/{pago_info['telefono']}?text={urllib.parse.quote(pago_info['mensaje_wa'])}"
            st.markdown(f"[📲 **Reenviar Comprobante por WhatsApp**]({wa_url_reprint})")
