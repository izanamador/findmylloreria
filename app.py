import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import folium
from streamlit_folium import st_folium
import sqlite3

# --- CONFIGURACIÓN BÁSICA ---
st.set_page_config(page_title="Find My Llorería", page_icon="😭", layout="wide")

# --- TÍTULO Y DESCRIPCIÓN VIRAL ---
st.markdown("<h1 style='text-align: center;'>🌧️ Find My Llorería 😭</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Los mejores lugares para llorar cerca de ti 💔📍</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Porque a veces el corazón duele y necesitas una buena vista para tus lágrimas. Llora con estilo. Llora con mapa. 🗺️💦</p>", unsafe_allow_html=True)

# --- CONEXIÓN A LA BBDD ---
conn = sqlite3.connect("cryingstops_db", check_same_thread=False)
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS spots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lat REAL,
        lon REAL,
        title TEXT,
        notes TEXT
    )
""")
conn.commit()

# --- GEOLOCALIZACIÓN ---
location = streamlit_geolocation()

if location and location["latitude"] and location["longitude"]:
    latitude = location["latitude"]
    longitude = location["longitude"]
    st.markdown("<p style='text-align: center; color: green;'>📍 Ubicación detectada correctamente</p>", unsafe_allow_html=True)
else:
    st.markdown("""
        <script>
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    window.parent.postMessage({type: 'setLocation', latitude: lat, longitude: lon}, "*");
                });
            }
        </script>
    """, unsafe_allow_html=True)

    st.markdown("<p style='text-align: center; color: orange;'>⚠️ No se pudo obtener la ubicación. Mostrando Madrid por defecto. Asegúrate de tener activado el GPS y dar permisos. 🧭</p>", unsafe_allow_html=True)
    latitude = 40.4168
    longitude = -3.7038

# --- CARGAR LUGARES DESDE LA BBDD ---
c.execute("SELECT lat, lon, title, notes FROM spots")
saved_places = c.fetchall()

# --- CREAR LAS COLUMNAS PARA ORGANIZAR EL CONTENIDO ---
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    # --- MAPA ---
    m = folium.Map(location=[latitude, longitude], zoom_start=13)

    # Marcador de tu ubicación
    folium.Marker(
        [latitude, longitude],
        popup="📍 Aquí lloras tú",
        icon=folium.Icon(color="blue", icon="user")
    ).add_to(m)

    # Añadir lugares guardados
    for lat, lon, title, notes in saved_places:
        folium.Marker(
            location=[lat, lon],
            popup=f"<strong>{title}</strong><br>{notes}",
            icon=folium.Icon(color="purple", icon="heart")
        ).add_to(m)

    # Mostrar el mapa y capturar clics
    map_data = st_folium(m, width=800, height=500)

    # --- AÑADIR LUGAR NUEVO SI HACES CLIC ---
    if map_data and map_data.get("last_clicked"):
        clicked_lat = map_data["last_clicked"]["lat"]
        clicked_lon = map_data["last_clicked"]["lng"]

        with st.expander("➕ Añadir una nueva llorería"):
            title = st.text_input("Nombre del lugar", key="title")
            notes = st.text_area("¿Qué lo hace tan llorable?", key="notes")
            if st.button("💾 Guardar mi llorería"):
                c.execute("INSERT INTO spots (lat, lon, title, notes) VALUES (?, ?, ?, ?)",
                          (clicked_lat, clicked_lon, title, notes))
                conn.commit()
                st.success("✅ Llorería guardada. ¡No olvides llevar pañuelos!")
                st.rerun()

# Columnas vacías para centrado
with col1:
    st.write("")

with col3:
    st.write("")
