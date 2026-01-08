import streamlit as st
import pandas as pd
from sqlalchemy import text

from app.database import get_engine

st.set_page_config(page_title="Admin Panel", page_icon="🛠️")
st.title("🛠️ Panel de Administración")

# --- 1. SEGURIDAD ---
secret_pass = st.sidebar.text_input("Contraseña de Admin", type="password")

if secret_pass != "simplemente, juego de caballeros":
    st.info("Introduce la contraseña para acceder a las herramientas de gestión.")
    st.stop() # Detiene la ejecución aquí si no hay clave

engine = get_engine()

# --- 2. GESTIÓN DE JUGADORES ---
st.header("🎩 Gestión de Caballeros")

with st.form("new_player_form", clear_on_submit=True):
    # Datos del nuevo jugador
    col1, col2 = st.columns(2)
    new_name = col1.text_input("Nombre")
    new_nick = col2.text_input("Nickname")
    new_borne = col1.date_input("Fecha de Nacimiento")
    new_favgame = col2.selectbox("Juego Favorito", ["Catan", "Splendor", "Survive the Island", "Jugar con tu señora"])
    new_ownedgames = col1.number_input("Número de Juegos Propios", min_value=0, step=1)
    new_role = col2.text_input("Rol en la Mesa (ej: Jugador, Espectador, Bartender, Cocinero, etc.)")

    submitted = st.form_submit_button("Ingresar Caballero a la Mesa 🎲")
    
    if submitted:
        if new_name and new_nick:
            try:
                with engine.connect() as conn:
                    # Usamos parámetros (:name) para evitar inyección SQL (seguridad básica)
                    query = text("INSERT INTO players (name, nickname, active, created_at) VALUES (:n, :nick, TRUE, NOW())")
                    conn.execute(query, {"n": new_name, "nick": new_nick})
                    conn.commit()
                st.success(f"Bienvenido mi estimado {new_nick}, es todo un honor.")
            except Exception as e:
                st.error(f"Error al crear jugador: {e}")
        else:
            st.warning("Por favor completa todos los campos.")

# --- 3. VER JUGADORES ACTUALES ---
st.subheader("Lista de Jugadores Activos")
with engine.connect() as conn:
    df_players = pd.read_sql("SELECT player_id, name, nickname, created_at FROM players WHERE active = TRUE ORDER BY created_at DESC", conn)
    st.dataframe(df_players, hide_index=True)