import streamlit as st
import pandas as pd
from sqlalchemy import text
from datetime import date
# Importamos el engine desde el módulo compartido
from app.database import get_engine 

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Noches de Caballeros", page_icon="⚔️", layout="wide")

# Obtenemos la conexión
engine = get_engine()

# --- TÍTULO ---
st.title("⚔️ Noches de Caballeros: The Leaderboard")

# CREAMOS LAS PESTAÑAS
tab_carga, tab_stats, tab_historial = st.tabs(["📝 Cargar Partida", "🏆 Salón de la Fama", "📜 Historial"])

# ==============================================================================
# PESTAÑA 1: CARGA DE DATOS (Tu código anterior, encapsulado)
# ==============================================================================
with tab_carga:
    st.header("Registrar Nueva Batalla")
    
    # 1. Cargar datos auxiliares
    try:
        with engine.connect() as conn:
            df_players = pd.read_sql("SELECT player_id, name FROM players WHERE active = TRUE", conn)
            df_games = pd.read_sql("SELECT game_id, name FROM games", conn)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        st.stop()

    player_map = dict(zip(df_players['name'], df_players['player_id']))
    game_map = dict(zip(df_games['name'], df_games['game_id']))

    with st.form("entry_form"):
        col1, col2 = st.columns(2)
        with col1:
            session_date = st.date_input("Fecha", date.today())
            host_name = st.selectbox("Anfitrión", options=df_players['name'])
        with col2:
            game_name = st.selectbox("Juego", options=df_games['name'])
            win_type = st.select_slider("Tipo de Victoria", options=["Normal", "Paliza", "Clutch (Sufrida)"])

        st.divider()
        players_selected = st.multiselect("Jugadores", options=df_players['name'])
        winner_name = st.selectbox("Ganador", options=players_selected if players_selected else df_players['name'])
        
        submitted = st.form_submit_button("💾 Guardar Partida")

    if submitted:
        if not players_selected:
            st.warning("⚠️ Selecciona jugadores.")
        elif winner_name not in players_selected:
            st.error("⚠️ El ganador debe haber jugado.")
        else:
            try:
                with engine.connect() as conn:
                    with conn.begin():
                        # 1. Crear Sesión
                        q_sess = text("INSERT INTO sessions (date, host_id) VALUES (:d, :h) RETURNING session_id")
                        sess_id = conn.execute(q_sess, {"d": session_date, "h": player_map[host_name]}).fetchone()[0]
                        
                        # 2. Crear Match
                        q_match = text("INSERT INTO matches (session_id, game_id, winner_id, win_type) VALUES (:s, :g, :w, :wt) RETURNING match_id")
                        match_id = conn.execute(q_match, {"s": sess_id, "g": game_map[game_name], "w": player_map[winner_name], "wt": win_type}).fetchone()[0]
                        
                        # 3. Participantes
                        q_part = text("INSERT INTO match_participants (match_id, player_id, rank) VALUES (:m, :p, :r)")
                        for p in players_selected:
                            rank = 1 if p == winner_name else 2
                            conn.execute(q_part, {"m": match_id, "p": player_map[p], "r": rank})
                            
                st.success("✅ Partida registrada correctamente")
                st.balloons()
            except Exception as e:
                st.error(f"Error al guardar: {e}")

# ==============================================================================
# PESTAÑA 2: ESTADÍSTICAS
# ==============================================================================
with tab_stats:
    st.header("📊 Estadísticas Generales")
    
    # QUERY: Calcula todo en SQL directamente
    sql_stats = """
    SELECT 
        p.name as "Caballero",
        COUNT(mp.match_id) as "Partidas Jugadas",
        SUM(CASE WHEN mp.rank = 1 THEN 1 ELSE 0 END) as "Victorias",
        SUM(CASE WHEN mp.rank = 2 THEN 1 ELSE 0 END) as "Subcampeonatos"
    FROM players p
    JOIN match_participants mp ON p.player_id = mp.player_id
    GROUP BY p.name
    ORDER BY "Victorias" DESC, "Subcampeonatos" DESC
    """
    
    try:
        with engine.connect() as conn:
            df_stats = pd.read_sql(sql_stats, conn)
            
        if not df_stats.empty:
            # Cálculo de Win Rate con Pandas
            df_stats["Win Rate %"] = ((df_stats["Victorias"] / df_stats["Partidas Jugadas"]) * 100).round(1)
            
            # KPI Cards (Top Metrics)
            col1, col2, col3 = st.columns(3)
            
            top_winner = df_stats.iloc[0]
            col1.metric("👑 El Rey Actual", top_winner["Caballero"], f"{int(top_winner['Victorias'])} Victorias")
            
            cebollitas = df_stats.sort_values("Subcampeonatos", ascending=False).iloc[0]
            col2.metric("🧅 Premio Cebollita", cebollitas["Caballero"], f"{int(cebollitas['Subcampeonatos'])} Segundos puestos")
            
            mas_activo = df_stats.sort_values("Partidas Jugadas", ascending=False).iloc[0]
            col3.metric("⚔️ El Más Activo", mas_activo["Caballero"], f"{int(mas_activo['Partidas Jugadas'])} Partidas")
            
            st.divider()
            
            # Tabla Principal
            st.subheader("Tabla de Posiciones")
            # Reordenamos columnas para que quede lindo
            st.dataframe(
                df_stats[["Caballero", "Victorias", "Win Rate %", "Subcampeonatos", "Partidas Jugadas"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Aún no hay suficientes datos para generar estadísticas. ¡Jueguen algo!")
            
    except Exception as e:
        st.error(f"Error calculando stats: {e}")

# ==============================================================================
# PESTAÑA 3: HISTORIAL
# ==============================================================================
with tab_historial:
    st.header("📜 Historial de Batallas")
    try:
        with engine.connect() as conn:
            historial = pd.read_sql("""
                SELECT m.match_id, s.date as Fecha, g.name as Juego, p.name as Ganador, m.win_type
                FROM matches m
                JOIN games g ON m.game_id = g.game_id
                JOIN players p ON m.winner_id = p.player_id
                JOIN sessions s ON m.session_id = s.session_id
                ORDER BY m.match_id DESC
            """, conn)
            st.dataframe(historial, hide_index=True, use_container_width=True)
    except Exception as e:
        st.error(f"Error: {e}")
