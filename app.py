import streamlit as st
import pandas as pd

# -----------------------------
# Configuración de la página
# -----------------------------
st.set_page_config(
    page_title="Consulta Excel",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Estilos (CSS simple)
# -----------------------------
st.markdown("""
<style>
    .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
    h1 { margin-bottom: 0.2rem; }
    .small-note { color: rgba(255,255,255,0.65); font-size: 0.9rem; margin-top: -0.2rem; }
    .card { padding: 1rem; border: 1px solid rgba(255,255,255,0.10); border-radius: 12px; background: rgba(255,255,255,0.03); }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Encabezado
# -----------------------------
st.title("🔎 Clasificador de bienes y servicios - Códigos UNSPSC")
st.markdown('<div class="small-note">Sube tu archivo, elige el campo y busca por palabra o valor exacto.</div>', unsafe_allow_html=True)
st.write("")

# -----------------------------
# Sidebar: Carga + Controles
# -----------------------------
with st.sidebar:
    st.header("📂 Archivo y búsqueda")

    archivo = st.file_uploader("Sube el archivo Excel", type=["xlsx"])

    st.divider()

    # Controles: aparecen cuando ya hay archivo
    if archivo is not None:
        opciones_busqueda = ["Contiene (recomendado)", "Coincide exacto"]
        modo = st.selectbox("Tipo de búsqueda", opciones_busqueda, index=0)

        ignorar_mayus = st.checkbox("Ignorar mayúsculas/minúsculas", value=True)
        mostrar_vista_previa = st.checkbox("Mostrar vista previa", value=True)

        st.divider()
        st.caption("Tip: si buscas por código, usa 'Coincide exacto'.")

    st.divider()
    limpiar = st.button("🧹 Limpiar búsqueda", use_container_width=True)

# -----------------------------
# Carga del Excel
# -----------------------------
if archivo is None:
    st.info("📌 Sube un archivo Excel para comenzar.")
    st.stop()

# Lee excel
try:
    df = pd.read_excel(archivo)
except Exception as e:
    st.error(f"❌ No se pudo leer el archivo. Detalle: {e}")
    st.stop()

if df.empty:
    st.warning("⚠️ El archivo se cargó, pero no contiene filas.")
    st.stop()

# Limpieza básica de columnas vacías
df = df.loc[:, ~df.columns.astype(str).str.contains("^Unnamed")]

# -----------------------------
# Controles principales (en el cuerpo, pero compactos)
# -----------------------------
colA, colB, colC = st.columns([2.2, 2.2, 2.6], vertical_alignment="bottom")

with colA:
    columna = st.selectbox("🔽 Campo de búsqueda", df.columns)

with colB:
    valor = st.text_input("✍️ Valor a buscar", placeholder="Ej: mantenimiento, 1010, roedores...")

with colC:
    st.markdown('<div class="card">📌 Sugerencia: para textos, usa palabras clave. Para códigos, pega el número exacto.</div>', unsafe_allow_html=True)

# Limpiar: borra el texto (reinicia el estado)
if limpiar:
    st.rerun()

st.write("")

# -----------------------------
# Pestañas: Resultados / Vista previa
# -----------------------------
tab1, tab2 = st.tabs(["✅ Resultados", "👀 Vista previa"])

# -----------------------------
# Resultados
# -----------------------------
with tab1:
    if not valor:
        st.info("Escribe un valor para buscar y ver los resultados.")
        st.stop()

    # Preparación
    serie = df[columna].astype(str)

    # Búsqueda
    if modo == "Coincide exacto":
        if ignorar_mayus:
            mask = serie.str.lower().str.strip() == str(valor).lower().strip()
        else:
            mask = serie.str.strip() == str(valor).strip()
    else:  # Contiene
        if ignorar_mayus:
            mask = serie.str.contains(str(valor), case=False, na=False)
        else:
            mask = serie.str.contains(str(valor), case=True, na=False)

    resultados = df[mask]

    # Layout de resultados
    topL, topR = st.columns([1, 3], vertical_alignment="center")
    with topL:
        st.metric("Registros encontrados", int(len(resultados)))
    with topR:
        st.caption("Puedes copiar/filtrar dentro de la tabla. Si el archivo es grande, reduce la búsqueda.")

    if resultados.empty:
        st.warning("❌ No se encontraron resultados. Prueba con otra columna o una palabra más corta.")
    else:
        st.dataframe(resultados, use_container_width=True, hide_index=True)

# -----------------------------
# Vista previa
# -----------------------------
with tab2:
    if 'mostrar_vista_previa' in locals() and mostrar_vista_previa:
        st.subheader("👀 Vista previa de los datos")
        st.dataframe(df.head(50), use_container_width=True, hide_index=True)
        st.caption("Mostrando las primeras 50 filas para no saturar la interfaz.")
    else:
        st.info("Activa 'Mostrar vista previa' en el panel izquierdo si deseas verla.")

# -----------------------------
# Footer - Powered by
# -----------------------------
st.markdown("""
<style>
.footer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background-color: rgba(0, 0, 0, 0.6);
    color: #cfcfcf;
    text-align: center;
    padding: 6px 0;
    font-size: 0.85rem;
    z-index: 999;
}
</style>

<div class="footer">
    Powered by <strong>Streamlit</strong> · Developed by <strong>David Gálvez</strong>
</div>
""", unsafe_allow_html=True)
