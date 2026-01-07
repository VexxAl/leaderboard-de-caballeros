import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Noche de Caballeros", page_icon="⚔️")

st.title("⚔️ Leaderboard: Noche de Caballeros")

# Cargar variables del archivo .env
load_dotenv()

# Construir la URL usando las variables ocultas
# Si no encuentra las variables, usa valores por defecto (seguridad)
db_user = os.getenv("DB_USER", "admin")
db_pass = os.getenv("DB_PASSWORD", "password123")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5433")
db_name = os.getenv("DB_NAME", "leaderboard_db")

DB_URL = f"postgresql+pg8000://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

@st.cache_resource
def get_connection():
    try:
        engine = create_engine(DB_URL)
        # Probamos conexión simple
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        st.error(f"❌ Error conectando a la BD: {e}")
        return None

engine = get_connection()

if engine:
    st.success("✅ ¡Conexión con PostgreSQL exitosa!")

    # --- CONSULTA DE PRUEBA ---
    st.subheader("Jugadores Registrados (Seed Data)")
    
    try:
        # Leemos la tabla players usando Pandas + SQL
        df_players = pd.read_sql("SELECT * FROM players", engine)
        
        # Mostramos la tabla bonita en Streamlit
        st.dataframe(
            df_players, 
            hide_index=True,
            column_config={
                "player_id": "ID",
                "name": "Nombre",
                "nickname": "Apodo",
                "active": "Activo",
                "created_at": "Fecha Alta"
            }
        )
    except Exception as e:
        st.error(f"Error leyendo datos: {e}")

else:
    st.warning("⚠️ Asegúrate que Docker esté corriendo con 'docker-compose up -d'")
