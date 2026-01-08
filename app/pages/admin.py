import streamlit as st
import pandas as pd
from sqlalchemy import text
import os
import random
import time
from dotenv import load_dotenv

from app.database import get_engine

load_dotenv()

st.set_page_config(page_title="Admin Dungeon", page_icon="🐉")

# --- GESTIÓN DE ESTADO (LA MEMORIA DEL JUEGO) ---
if 'dungeon_stage' not in st.session_state:
    st.session_state.dungeon_stage = 'door'  # Etapas: door, combat, loot, unlocked
if 'monster_hp' not in st.session_state:
    st.session_state.monster_hp = 50  # Vida del monstruo
if 'monster_max_hp' not in st.session_state:
    st.session_state.monster_max_hp = 50

# --- FUNCIONES DE LA MAZMORRA ---
def reset_dungeon():
    st.session_state.dungeon_stage = 'door'
    st.session_state.monster_hp = 50

# ==============================================================================
# 🏰 FASE 1: LA MAZMORRA (GAMIFICATION)
# ==============================================================================
if st.session_state.dungeon_stage != 'unlocked':
    st.title("🏰 La Mazmorra del Admin")
    
    # --- ESCENA 1: LA PUERTA ---
    if st.session_state.dungeon_stage == 'door':
        st.markdown("""
        Te encuentras frente a una puerta de madera reforzada con hierro. 
        Se escucha una respiración pesada del otro lado...
        """)
        st.image("https://img.icons8.com/color/96/closed-door.png", width=100)
        
        if st.button("🦵 PATEAR LA PUERTA (Tirar Fuerza)"):
            with st.spinner("Tomando carrera..."):
                time.sleep(1)
            st.session_state.dungeon_stage = 'combat'
            st.rerun()

    # --- ESCENA 2: EL COMBATE ---
    elif st.session_state.dungeon_stage == 'combat':
        st.error("¡Un BUG DE PRODUCCIÓN SALVAJE apareció!")
        
        # Barra de vida del monstruo
        hp_percent = st.session_state.monster_hp / st.session_state.monster_max_hp
        st.progress(hp_percent, text=f"Vida del Bug: {st.session_state.monster_hp}/{st.session_state.monster_max_hp}")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image("https://img.icons8.com/color/96/insect-robot.png", width=100)
        with col2:
            st.markdown(f"**¡Tira los dados para debuggear esta bestia!**")
            
            if st.button("🎲 Tirar D20 de Ataque"):
                damage = random.randint(1, 20)
                crit = damage == 20
                fail = damage == 1
                
                # Cálculo de daño (Critical hit hace doble)
                final_damage = damage * 2 if crit else damage
                if fail: final_damage = 0
                
                st.session_state.monster_hp -= final_damage
                
                # Feedback visual
                if crit:
                    st.toast(f"¡CRÍTICO! 💥 Hiciste {final_damage} de daño.", icon="🔥")
                elif fail:
                    st.toast("¡Pifia! 💩 Te tropezaste con el cable de red. 0 daño.", icon="🤡")
                else:
                    st.toast(f"¡Zas! ⚔️ {final_damage} de daño.", icon="🗡️")
                
                # Verificar muerte
                if st.session_state.monster_hp <= 0:
                    st.session_state.dungeon_stage = 'loot'
                    st.balloons()
                
                st.rerun()

    # --- ESCENA 3: EL LOOT Y EL ACERTIJO ---
    elif st.session_state.dungeon_stage == 'loot':
        st.success("¡El Bug ha sido eliminado! Soltó un cofre legendario.")
        st.image("https://img.icons8.com/color/96/treasure-chest.png", width=100)
        
        st.markdown("### 📜 El Pergamino de la Verdad")
        st.caption("Para abrir el panel, responde el acertijo del guardián:")
        
        riddle = st.text_input("Tengo ciudades, pero no casas. Tengo montañas, pero no árboles. Tengo agua, pero no peces. ¿Qué soy?")
        
        if st.button("Abrir Cofre"):
            if riddle.strip().lower() in ["mapa", "un mapa", "el mapa", "catan", "tablero"]:
                st.success("¡El cofre se abre!")
                st.session_state.dungeon_stage = 'unlocked'
                st.rerun()
            else:
                st.error("El cofre permanece cerrado. Intenta de nuevo.")

# ==============================================================================
# 🛠️ FASE 2: EL PANEL REAL (SOLO SI SE PASÓ LA MAZMORRA)
# ==============================================================================
else:
    # --- AQUÍ EMPIEZA TU CÓDIGO ORIGINAL DE ADMIN ---
    
    # Botón para salir (Logout del juego)
    if st.sidebar.button("🔒 Bloquear Panel"):
        reset_dungeon()
        st.rerun()

    st.title("🛠️ Panel de Administración")
    
    # Recuperamos la contraseña real del entorno
    real_admin_pass = os.getenv("ADMIN_PASSWORD", "1234")
    
    st.info(f"🏆 ¡Bien jugado! La contraseña del sistema es: **{real_admin_pass}**")

    # --- 1. SEGURIDAD ---
    secret_pass = st.text_input("Ingresa la contraseña para confirmar acceso", type="password")

    if secret_pass != real_admin_pass:
        st.warning("Copia la contraseña de arriba, valiente aventurero.")
        st.stop() 

    engine = get_engine()

    # CREAMOS LAS PESTAÑAS
    tab_caballeros, tab_juegos = st.tabs(["🎩 Gestión de Caballeros", "🃏 Carga de Juegos"])

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
            col1, col2 = st.columns(2)
            new_name = col1.text_input("Nombre")
            new_nick = col2.text_input("Nickname")
            new_birth = col1.date_input("Fecha de Nacimiento")
            new_favgame = col2.selectbox("Juego Favorito", options=df_games['name'] if not df_games.empty else ["Sin juegos"])
            new_ownedgames = col1.number_input("Número de Juegos Propios", min_value=0, step=1)
            new_role = col2.text_input("Rol en la Mesa (ej: Jugador, Bartender, Cocinero)")

            submitted = st.form_submit_button("Ingresar Caballero a la Mesa 🎲")
            
            if submitted:
                if new_name and new_nick and not df_games.empty:
                    try:
                        favgame_id = game_map[new_favgame]
                        with engine.connect() as conn:
                            query = text("""
                                INSERT INTO players (name, nickname, birth_date, favgame_id, owned_games, role, active, created_at) 
                                VALUES (:n, :nick, :b, :f, :o, :r, TRUE, NOW())
                            """)
                            conn.execute(query, {
                                "n": new_name, "nick": new_nick, "b": new_birth,
                                "f": favgame_id, "o": new_ownedgames, "r": new_role
                            })
                            conn.commit()
                        st.success(f"Bienvenido mi estimado {new_nick}, es todo un honor.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error al crear jugador: {e}")
                else:
                    st.warning("Faltan datos o no hay juegos cargados.")

        # VER JUGADORES
        st.divider()
        st.subheader("Lista de Jugadores Activos")
        with engine.connect() as conn:
            df_view = pd.read_sql("""
                SELECT p.name, p.nickname, p.role, g.name AS favorite_game, p.owned_games 
                FROM players p LEFT JOIN games g ON p.favgame_id = g.game_id 
                WHERE p.active = TRUE ORDER BY p.created_at DESC
            """, conn)
            st.dataframe(df_view, hide_index=True, use_container_width=True)

    # PESTAÑA 2: CARGA DE JUEGOS
    with tab_juegos:
        st.header("🃏 Carga de Nuevos Juegos")
        with st.form("new_game_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            new_logo = col1.text_input("Emoji", value="🎲")
            new_game_name = col2.text_input("Nombre del Juego")
            new_game_minplayers = col1.number_input("Mínimo Jugadores", 1, step=1)
            new_game_maxplayers = col2.number_input("Máximo Jugadores", 1, step=1)
            new_type = col1.selectbox("Tipo", ["Principal", "Casual", "Party Game", "co-op", "Cartas"])
            new_owner = col2.selectbox("Dueño", options=df_players['name'] if not df_players.empty else ["Sin jugadores"])

            submitted_game = st.form_submit_button("Agregar Juego 📚")

            if submitted_game:
                if new_game_name and not df_players.empty:
                    try:
                        owner_id = player_map[new_owner]
                        with engine.connect() as conn:
                            query = text("""
                                INSERT INTO games (name, logo, min_players, max_players, type, owner_id) 
                                VALUES (:n, :l, :minp, :maxp, :t, :o)
                            """)
                            conn.execute(query, {
                                "n": new_game_name, "l": new_logo, "minp": new_game_minplayers,
                                "maxp": new_game_maxplayers, "t": new_type, "o": owner_id
                            })
                            conn.commit()
                        st.success(f"'{new_game_name}' agregado exitosamente.")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Datos incompletos.")
