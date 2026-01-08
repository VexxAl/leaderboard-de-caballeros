import os
import streamlit as st
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Carga variables del archivo .env si existe
load_dotenv()

def get_db_url():
    """Construye la URL de conexión leyendo el entorno."""
    user = os.getenv("DB_USER", "admin")
    password = os.getenv("DB_PASSWORD", "password123")
    host = os.getenv("DB_HOST", "localhost") 
    port = os.getenv("DB_PORT", "5432")      
    name = os.getenv("DB_NAME", "leaderboard_db")
    
    return f"postgresql+pg8000://{user}:{password}@{host}:{port}/{name}"

@st.cache_resource
def get_engine():
    """Crea y cachea la conexión para no abrir una nueva con cada clic."""
    url = get_db_url()
    return create_engine(url)