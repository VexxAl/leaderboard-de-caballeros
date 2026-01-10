import streamlit as st
import pandas as pd
from sqlalchemy import text
from datetime import date

from app.database import get_engine 

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Noches de Caballeros", page_icon="⚔️", layout="wide")

# Obtenemos la conexión
engine = get_engine()

# --- TÍTULO ---
st.title("⚔️ Juegos de Caballeros: The Leaderboard")

# --- NAVEGACIÓN ---
col_nav1, col_nav2 = st.columns([6, 1])
with col_nav2:
    if st.button("📜 Ver Reglas"):
        st.switch_page("pages/rules.py")

# CREAMOS LAS PESTAÑAS
tab_sesion, tab_partida, tab_stats, tab_historial = st.tabs(["🫱🏻‍🫲🏻 Nueva Sesión", "📝 Cargar Partida", "🏆 Salón de la Fama", "📜 Historial"])

# ==============================================================================
# PESTAÑA 1: NUEVA SESIÓN
# ==============================================================================
with tab_sesion:
    st.header("Planificar la Noche 🌙")
    st.caption("Primero crea la juntada, luego carga las partidas en la siguiente pestaña.")
    
    # Traemos los anfitriones (nicknames)
    try:
        with engine.connect() as conn:
            query_hosts = """
                SELECT nickname, player_id 
                FROM players 
                WHERE active = TRUE OR role = 'Sede' 
                ORDER BY nickname ASC
            """
            df_hosts = pd.read_sql(query_hosts, conn)
    except Exception as e:
        st.error("Error de conexión.")
        st.stop()
    
    # Mapa de hosts existentes
    host_map = dict(zip(df_hosts['nickname'], df_hosts['player_id']))

    # Preparamos la lista del desplegable agregando la opción de crear uno nuevo
    lista_hosts = df_hosts['nickname'].tolist()
    opcion_nuevo = "➕ Nuevo Lugar / Anfitrión..."
    lista_hosts.append(opcion_nuevo)

    with st.form("session_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            sess_date = st.date_input("Fecha de la Juntada", date.today())
            sess_host = st.selectbox("Anfitrión / Lugar", options=lista_hosts)

            # Si eligen crear nuevo, mostramos el input de texto
            new_host_name = None
            if sess_host == opcion_nuevo:
                new_host_name = st.text_input("Nombre del Nuevo Lugar", placeholder="Ej: Bar Temple, Casa de Juan...")
                st.caption("Este lugar se guardará en la base de datos para futuras juntadas.")

            sess_attendees = st.number_input("Cantidad de Personas (Total)", min_value=1, value=4, step=1)
        
        with col2:
            sess_food = st.text_input("Comida", placeholder="Ej: Pizzas a la parrilla, Asado, Empanadas...")
            sess_cost = st.number_input("Gasto por cabeza ($)", min_value=0, step=1000)

        submit_session = st.form_submit_button("🧝🏻‍♂️ Iniciar Cofradía de Caballeros")
    
    if submit_session:
        try:
            with engine.connect() as conn:
                # Verificamos si ya existe una sesión esa fecha
                check_query = text("SELECT session_id FROM sessions WHERE date = :d")
                existing = conn.execute(check_query, {"d": sess_date}).fetchone()
                
                if existing:
                    st.warning(f"Ya existe una cofradía registrada para el {sess_date.strftime('%d/%m/%Y')}. Ve a 'Cargar Partida' o usa otra fecha.")
                else:
                    # Si es nuevo host, lo insertamos primero
                    final_host_id = None
                    final_host_name = ""

                    if sess_host == opcion_nuevo:
                        if new_host_name:
                            # Insertar nuevo host
                            insert_host_query = text("""
                                INSERT INTO players (name, nickname, role, active, created_at, owned_games)
                                VALUES (:n, :n, 'Sede', FALSE, NOW(), 0) 
                                RETURNING player_id
                            """)
                            result = conn.execute(insert_host_query, {"n": new_host_name})
                            final_host_id = result.fetchone()[0]
                            final_host_name = new_host_name
                        else:
                            st.error("Debes ingresar un nombre para el nuevo lugar.")
                            st.stop()
                    else:
                        final_host_id = host_map[sess_host]
                        final_host_name = sess_host
                    
                    insert_query = text("""
                        INSERT INTO sessions (date, host_id, food, cost_per_person, total_attendees)
                        VALUES (:d, :h, :f, :c, :a)
                    """)
                    conn.execute(insert_query, {
                        "d": sess_date,
                        "h": host_map[sess_host],
                        "f": sess_food,
                        "c": sess_cost,
                        "a": sess_attendees
                    })
                    conn.commit()
                    st.success(f"Cofradía iniciada en casa de {sess_host}! Ahora pueden cargar partidas.")
                    st.balloons()
        except Exception as e:
            st.error(f"Error: {e}")
   
# ==============================================================================
# PESTAÑA 2: CARGA DE DATOS
# ==============================================================================

with tab_partida:
    st.header("Registrar Nueva Batalla 🗡️🏹")
    

    # 1. Cargar datos auxiliares
    try:
        with engine.connect() as conn:
            # 1. Traer Sesiones Disponibles (Últimas 10)
            # Mostramos: "Fecha - Casa de [Host]"
            sessions_query = """
                SELECT s.session_id, s.date, p.nickname as host 
                FROM sessions s
                JOIN players p ON s.host_id = p.player_id
                ORDER BY s.date DESC LIMIT 10
            """
            df_sessions = pd.read_sql(sessions_query, conn)

            df_players = pd.read_sql("SELECT player_id, nickname FROM players WHERE active = TRUE", conn)
            df_games = pd.read_sql("SELECT game_id, name FROM games WHERE name <> 'Jugar con tu señora'", conn)
    except Exception as e:
        st.error(f"Error cargando listas: {e}")
        st.stop()

    if df_sessions.empty:
        st.warning("No hay sesiones activas. Crea una en la pestaña 'Nueva Sesión' antes de cargar partidas.")
    else:
        # Crear lista legible para el dropdown de sesiones
        df_sessions['label'] = df_sessions.apply(lambda x: f"{x['date'].strftime('%d/%m/%Y')} - 📍 {x['host']}", axis=1)
        session_map = dict(zip(df_sessions['label'], df_sessions['session_id']))
        
        player_map = dict(zip(df_players['nickname'], df_players['player_id']))
        game_map = dict(zip(df_games['name'], df_games['game_id']))

        with st.form("match_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # AQUÍ SELECCIONAN LA SESIÓN POR FECHA
                selected_session_label = st.selectbox("Seleccionar Juntada", options=df_sessions['label'])
                game_name = st.selectbox("Juego", options=df_games['name'])
            
            with col2:
                duration = st.number_input("Duración (minutos) ⏱️", min_value=5, value=45, step=5)
                win_type = st.select_slider("Intensidad", options=["Normal", "Clutch (Sufrida)", "Paliza"], value="Normal")

            st.divider()
            players_selected = st.multiselect("Jugadores en la mesa", options=df_players['nickname'])
            winner_name = st.selectbox("Ganador", options=players_selected if players_selected else ["Selecciona jugadores primero"])
            
            submitted_match = st.form_submit_button("💾 Guardar Resultado")

        if submitted_match:
            if not players_selected:
                st.warning("⚠️ Faltan jugadores.")
            elif winner_name not in players_selected:
                st.error("⚠️ El ganador debe estar en la mesa.")
            else:
                try:
                    session_id = session_map[selected_session_label]
                    game_id = game_map[game_name]
                    winner_id = player_map[winner_name]
                    
                    with engine.connect() as conn:
                        with conn.begin():
                            # Insertar Match con Duración
                            q_match = text("""
                                INSERT INTO matches (session_id, game_id, winner_id, win_type, duration_minutes) 
                                VALUES (:s, :g, :w, :wt, :dur) RETURNING match_id
                            """)
                            match_id = conn.execute(q_match, {
                                "s": session_id, "g": game_id, "w": winner_id, "wt": win_type, "dur": duration
                            }).fetchone()[0]
                            
                            # Insertar Participantes
                            q_part = text("INSERT INTO match_participants (match_id, player_id, rank) VALUES (:m, :p, :r)")
                            for p in players_selected:
                                rank = 1 if p == winner_name else 2
                                conn.execute(q_part, {"m": match_id, "p": player_map[p], "r": rank})
                                
                    st.success("✅ Partida registrada! Seguimos jugando...")
                except Exception as e:
                    st.error(f"Error grabando partida: {e}")

# ==============================================================================
# PESTAÑA 3: ESTADÍSTICAS
# ==============================================================================
with tab_stats:
    st.header("Estadísticas Generales 📊")
    
    # QUERY: Calcula todo en SQL directamente
    sql_stats = """
    SELECT 
        p.nickname as "Caballero",
        COUNT(mp.match_id) as "Partidas Jugadas",
        SUM(CASE WHEN mp.rank = 1 THEN 1 ELSE 0 END) as "Victorias",
        SUM(CASE WHEN mp.rank = 2 THEN 1 ELSE 0 END) as "Subcampeonatos"
    FROM players p
    JOIN match_participants mp ON p.player_id = mp.player_id
    GROUP BY p.nickname
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
# PESTAÑA 4: HISTORIAL
# ==============================================================================
with tab_historial:
    st.header("Historial de Batallas 📜")
    try:
        with engine.connect() as conn:
            historial = pd.read_sql("""
                SELECT m.match_id, s.date as Fecha, g.name as Juego, p.nickname as Ganador, m.win_type
                FROM matches m
                JOIN games g ON m.game_id = g.game_id
                JOIN players p ON m.winner_id = p.player_id
                JOIN sessions s ON m.session_id = s.session_id
                ORDER BY m.match_id DESC
            """, conn)
            st.dataframe(historial, hide_index=True, use_container_width=True)
    except Exception as e:
        st.error(f"Error: {e}")
