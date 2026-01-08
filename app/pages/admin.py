import streamlit as st
import pandas as pd
from sqlalchemy import text
import os
from dotenv import load_dotenv

from app.database import get_engine

load_dotenv()  

st.set_page_config(page_title="Admin Panel", page_icon="🛠️")
st.title("🛠️ Panel de Administración")

# --- 1. SEGURIDAD ---
secret_pass = st.text_input("Contraseña de Admin", type="password")

if secret_pass != os.getenv("ADMIN_PASSWORD"):
    st.info("Introduce la contraseña para acceder a las herramientas de gestión.")
    st.stop() # Detiene la ejecución aquí si no hay clave

engine = get_engine()

# CREAMOS LAS PESTAÑAS
tab_caballeros, tab_juegos = st.tabs(["🎩 Gestión de Caballeros", "🃏 Carga de Juegos"])

# --- 2. GESTIÓN ---

# Cargar datos auxiliares
try:
    with engine.connect() as conn:
        df_players = pd.read_sql("SELECT player_id, name FROM players WHERE active = TRUE", conn)
        df_games = pd.read_sql("SELECT game_id, name FROM games", conn)
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

player_map = dict(zip(df_players['name'], df_players['player_id']))
game_map = dict(zip(df_games['name'], df_games['game_id']))

# PESTAÑA 1: GESTIÓN DE CABALLEROS
with tab_caballeros:
    st.header("🎩 Gestión de Caballeros")

    with st.form("new_player_form", clear_on_submit=True):

        # Datos del nuevo jugador
        col1, col2 = st.columns(2)
        
        new_name = col1.text_input("Nombre")
        new_nick = col2.text_input("Nickname")
        
        new_birth = col1.date_input("Fecha de Nacimiento")
        new_favgame = col2.selectbox("Juego Favorito", options=df_games['name'])
        
        new_ownedgames = col1.number_input("Número de Juegos Propios", min_value=0, step=1)
        new_role = col2.text_input("Rol en la Mesa (ej: Jugador, Bartender, Cocinero)")

        submitted = st.form_submit_button("Ingresar Caballero a la Mesa 🎲")
        
        if submitted:
            # Validamos que al menos tenga nombre y nick
            if new_name and new_nick:
                try:
                    favgame_id = game_map[new_favgame]
                    with engine.connect() as conn:
                        query = text("""
                            INSERT INTO players (name, nickname, birth_date, favgame_id, owned_games, role, active, created_at) 
                            VALUES (:n, :nick, :b, :f, :o, :r, TRUE, NOW())
                        """)
                        
                        # Pasamos los valores del formulario al diccionario de parámetros
                        conn.execute(query, {
                            "n": new_name, 
                            "nick": new_nick,
                            "b": new_birth,
                            "f": favgame_id,
                            "o": new_ownedgames,
                            "r": new_role
                        })
                        conn.commit()
                    st.success(f"Bienvenido mi estimado {new_nick}, es todo un honor.")
                    st.balloons() # ¡Un poco de fiesta!
                except Exception as e:
                    st.error(f"Error al crear jugador: {e}")
            else:
                st.warning("Por favor, el Nombre y el Nickname son obligatorios.")

    # --- VER JUGADORES ACTUALES ---
    st.divider()
    st.subheader("Lista de Jugadores Activos")

    with engine.connect() as conn:
        # Actualizamos el SELECT para ver también los datos nuevos
        df_players = pd.read_sql("""
            SELECT p.name, p.nickname, p.role, g.name AS favorite_game, p.owned_games, p.birth_date
            FROM players p
            LEFT JOIN games g ON p.favgame_id = g.game_id
            WHERE p.active = TRUE                      
            ORDER BY p.created_at DESC
        """, conn)
        
        st.dataframe(df_players, hide_index=True, use_container_width=True)

# PESTAÑA 2: CARGA DE JUEGOS
with tab_juegos:
    st.header("🃏 Carga de Nuevos Juegos")

    with st.form("new_game_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        new_logo = col1.text_input("Emoji que lo Representa")
        new_game_name = col2.text_input("Nombre del Juego")
        
        new_game_minplayers = col1.number_input("Mínimo de Jugadores", min_value=1, step=1)
        new_game_maxplayers = col2.number_input("Máximo de Jugadores", min_value=1, step=1)
        
        new_type = col1.selectbox("Tipo de Juego", ["Principal", "Casual", "Party Game", "co-op", "Cartas", "CATAN"])
        new_owner = col2.selectbox("Dueño del Juego", options=df_players['name'])

        submitted_game = st.form_submit_button("Agregar Juego a la Ludoteca 📚")

        if submitted_game:
            if new_game_name and new_game_maxplayers >= new_game_minplayers:
                try:
                    owner_id = player_map[new_owner]
                    with engine.connect() as conn:
                        query = text("""
                            INSERT INTO games (name, logo, min_players, max_players, type, owner_id) 
                            VALUES (:n, :l, :minp, :maxp, :t, :o)
                        """)
                        conn.execute(query, {
                            "n": new_game_name,
                            "l": new_logo,
                            "minp": new_game_minplayers,
                            "maxp": new_game_maxplayers,
                            "t": new_type,
                            "o": owner_id
                        })
                        conn.commit()
                    st.success(f"'{new_game_name}' agregado exitosamente a la ludoteca.")
                except Exception as e:
                    st.error(f"Error al agregar juego: {e}")
            else:
                st.warning("Por favor, asegúrate de que el nombre del juego esté completo y que el máximo de jugadores sea mayor o igual al mínimo.")

    # --- VER JUEGOS ACTUALES ---
    st.divider()
    st.subheader("Lista de Juegos en la Ludoteca")
    with engine.connect() as conn:
        df_games = pd.read_sql("""
            SELECT g.logo, g.name, g.type, g.min_players, g.max_players, p.name AS owner 
            FROM games g
            LEFT JOIN players p ON g.owner_id = p.player_id
            ORDER BY g.name ASC
        """, conn)
        
        st.dataframe(df_games, hide_index=True, use_container_width=True)
