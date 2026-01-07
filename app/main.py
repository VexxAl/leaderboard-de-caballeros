import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import date
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
def get_engine():
    return create_engine(DB_URL)

engine = get_engine()

# --- FUNCIONES DE LECTURA (SELECT) ---
def get_players():
    with engine.connect() as conn:
        return pd.read_sql("SELECT player_id, name, nickname FROM players WHERE active = TRUE", conn)

def get_games():
    with engine.connect() as conn:
        return pd.read_sql("SELECT game_id, name, category FROM games", conn)

# --- INTERFAZ DE USUARIO ---
st.title("⚔️ Registrar Nueva Batalla")

# 1. Cargamos datos para los dropdowns
try:
    df_players = get_players()
    df_games = get_games()
except Exception as e:
    st.error(f"Error conectando a la DB: {e}")
    st.stop()

# Diccionarios para mapear Nombre -> ID (UX Friendly)
player_map = dict(zip(df_players['name'], df_players['player_id']))
game_map = dict(zip(df_games['name'], df_games['game_id']))

# --- FORMULARIO ---
with st.form("entry_form"):
    st.subheader("1. La Juntada (Session)")
    col1, col2 = st.columns(2)
    with col1:
        session_date = st.date_input("Fecha", date.today())
    with col2:
        host_name = st.selectbox("Anfitrión (Host)", options=df_players['name'])
    
    st.divider()
    
    st.subheader("2. La Partida (Match)")
    game_name = st.selectbox("Juego", options=df_games['name'])
    
    # Multiselect para elegir a TODOS los que jugaron
    players_selected = st.multiselect("Jugadores Involucrados", options=df_players['name'])
    
    # El ganador tiene que salir de la lista de los que jugaron
    winner_name = st.selectbox("Ganador", options=players_selected if players_selected else df_players['name'])
    
    win_type = st.select_slider("Tipo de Victoria", options=["Normal", "Paliza", "Clutch (Sufrida)"])
    
    submitted = st.form_submit_button("💾 Registrar en los Libros de Historia")

# --- LÓGICA DE GUARDADO (INSERT) ---
if submitted:
    if not players_selected:
        st.warning("⚠️ Debes seleccionar al menos un jugador.")
    elif winner_name not in players_selected:
        st.error(f"⚠️ El ganador ({winner_name}) debe estar entre los participantes.")
    else:
        # INICIO DE TRANSACCIÓN
        try:
            with engine.connect() as conn:
                with conn.begin(): # Esto inicia la transacción atómica
                    
                    # A. Crear Sesión y recuperar ID
                    query_session = text("""
                        INSERT INTO sessions (date, host_id) 
                        VALUES (:date, :host_id) 
                        RETURNING session_id
                    """)
                    result_session = conn.execute(query_session, {
                        "date": session_date, 
                        "host_id": player_map[host_name]
                    })
                    session_id = result_session.fetchone()[0]
                    
                    # B. Crear Match y recuperar ID
                    query_match = text("""
                        INSERT INTO matches (session_id, game_id, winner_id, win_type) 
                        VALUES (:session_id, :game_id, :winner_id, :win_type) 
                        RETURNING match_id
                    """)
                    result_match = conn.execute(query_match, {
                        "session_id": session_id,
                        "game_id": game_map[game_name],
                        "winner_id": player_map[winner_name],
                        "win_type": win_type
                    })
                    match_id = result_match.fetchone()[0]
                    
                    # C. Registrar Participantes (Loop)
                    query_participant = text("""
                        INSERT INTO match_participants (match_id, player_id, rank)
                        VALUES (:match_id, :player_id, :rank)
                    """)
                    
                    for p_name in players_selected:
                        p_id = player_map[p_name]
                        # Lógica simple de ranking: 1 si ganó, 2 si perdió (MVP)
                        rank = 1 if p_name == winner_name else 2
                        
                        conn.execute(query_participant, {
                            "match_id": match_id,
                            "player_id": p_id,
                            "rank": rank
                        })
                        
            st.success(f"✅ ¡Partida de {game_name} registrada con éxito!")
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Ocurrió un error al guardar: {e}")

# --- VISTA RÁPIDA DE ÚLTIMAS PARTIDAS ---
st.divider()
st.subheader("📜 Últimas Batallas")
try:
    with engine.connect() as conn:
        # Query Join para mostrar texto en lugar de IDs
        historial = pd.read_sql("""
            SELECT 
                m.match_id, 
                g.name as Juego, 
                p.name as Ganador, 
                m.win_type as "Tipo Victoria", 
                s.date as Fecha
            FROM matches m
            JOIN games g ON m.game_id = g.game_id
            JOIN players p ON m.winner_id = p.player_id  -- <--- AQUÍ ESTABA EL ERROR (antes decía p.winner_id)
            JOIN sessions s ON m.session_id = s.session_id
            ORDER BY m.match_id DESC LIMIT 5
        """, conn)
        st.dataframe(historial, hide_index=True)
except Exception as e:
    st.error(f"Error cargando el historial: {e}")
