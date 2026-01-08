import streamlit as st
import time
import random

# --- CONFIGURACIÓN DEL JUEGO ---
orc_insults = [
    "El Orco escupe cerveza: '¡Patético! ¡Ni para mover el ladrón servís!'",
    "¿Ese es tu ataque? ¡Mi gato juega mejor al Catán!",
    "'¡Tus estrategias son tan débiles como ese brazo!', ríe el Orco.",
    "¡Por los clavos de la puerta! ¿Quién te enseñó a pelear, un goblin manco?"
]

def init_dungeon_state():
    """Inicializa las variables de memoria si no existen."""
    if 'dungeon_stage' not in st.session_state:
        st.session_state.dungeon_stage = 'door'
    if 'monster_hp' not in st.session_state:
        st.session_state.monster_hp = 60
    if 'monster_max_hp' not in st.session_state:
        st.session_state.monster_max_hp = 60
    if 'combat_log' not in st.session_state:
        st.session_state.combat_log = []
    if 'has_fumbled_yet' not in st.session_state:
        st.session_state.has_fumbled_yet = False

def reset_dungeon():
    """Reinicia el juego para volver a jugar."""
    st.session_state.dungeon_stage = 'door'
    st.session_state.monster_hp = 60
    st.session_state.combat_log = []
    st.session_state.has_fumbled_yet = False

def render_dungeon():
    """Función principal que dibuja la mazmorra."""
    
    # 1. CSS Específico para la Mazmorra (Centrado y Estilo Dark)
    st.markdown("""
        <style>
        .centered-dungeon {
            text-align: center;
            padding: 20px;
            background-color: #1E1E1E;
            border-radius: 15px;
            margin-bottom: 20px;
            border: 2px solid #444;
        }
        .centered-dungeon img {
            margin-top: 20px;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.5);
        }
        .stButton button {
            margin: 0 auto;
            display: block;
        }
        .combat-log {
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #ccc;
            margin-top: 20px;
            text-align: left;
            background-color: #262626;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #555;
            max-height: 200px;
            overflow-y: auto;
        }
        </style>
    """, unsafe_allow_html=True)

    # 2. Inicializar estado
    init_dungeon_state()

    # 3. Estructura de Columnas (Centrado visual)
    col_spacer1, col_main, col_spacer2 = st.columns([1, 2, 1])
    
    with col_main:
        st.title("🏰 La Prueba del Guardián")
        
        # --- ETAPA 1: LA PUERTA ---
        if st.session_state.dungeon_stage == 'door':
            with st.container():
                st.markdown('<div class="centered-dungeon">', unsafe_allow_html=True)
                st.write("""
                Llevan horas recorriendo los pasillos húmedos de la mazmorra. El aire aquí es denso, cargado de un olor a moho antiguo y madera podrida. Frente a ustedes, el camino termina en una imponente puerta de roble reforzado.
                Del otro lado, no hay silencio. Se escucha una respiración pesada y el tic-tic-tic rítmico de algo golpeando madera.
                """)
                st.image("media/dungeon_door.png", width=120)
                st.write("Deciden entrar. El picaporte, frío al tacto, gira con un chirrido oxidado...")
                st.markdown('</div>', unsafe_allow_html=True)

            if st.button("Empujar la puerta 🚪"):
                with st.spinner("Abriendo..."):
                    time.sleep(2.5)
                st.session_state.dungeon_stage = 'reveal'
                st.rerun()

        # --- ETAPA 2: LA REVELACIÓN ---
        elif st.session_state.dungeon_stage == 'reveal':
             with st.container():
                st.markdown('<div class="centered-dungeon">', unsafe_allow_html=True)
                st.write("""
                La luz de las antorchas revela un caos: monedas de oro y joyas apartadas para hacer sitio a un tablero hexagonal.
                Y ahí está él. Un Orco masivo, cicatrizado, sentado y encorvado sobre el tablero. El lugar huele a cerveza rancia.
                Al notar la luz, el Orco levanta la vista con confusión, sosteniendo una carta de recurso arrugada. Parece estresado por su próximo movimiento.
                """)
                st.image("media/dungeon_orc.png", width=120)
                st.markdown('</div>', unsafe_allow_html=True)

             if st.button("¡Desafiar al Orco! ⚔️"):
                st.session_state.dungeon_stage = 'combat'
                st.rerun()

        # --- ETAPA 3: EL COMBATE ---
        elif st.session_state.dungeon_stage == 'combat':
            with st.container():
                st.markdown('<div class="centered-dungeon">', unsafe_allow_html=True)
                st.error("¡El Orco Ludópata ruge protegiendo sus ovejas!")
                st.image("https://img.icons8.com/color/96/fantasy.png", width=100)
                
                # Barra de vida
                hp_percent = st.session_state.monster_hp / st.session_state.monster_max_hp
                st.progress(hp_percent, text=f"Voluntad del Orco: {st.session_state.monster_hp}/{st.session_state.monster_max_hp}")
                st.markdown("---")
                
                if st.button("🎲 Tirar D20 de Ataque"):
                    # Lógica del destino (Pifia forzada)
                    force_fumble = (st.session_state.monster_hp < (st.session_state.monster_max_hp * 0.3)) and (not st.session_state.has_fumbled_yet)

                    if force_fumble:
                        damage = 1
                        st.session_state.has_fumbled_yet = True
                    else:
                        damage = random.randint(1, 20)
                        if damage == 1: st.session_state.has_fumbled_yet = True

                    crit = damage == 20
                    fail = damage == 1
                    final_damage = damage * 2 if crit else (0 if fail else damage)
                    
                    st.session_state.monster_hp -= final_damage
                    
                    # Feedback
                    log_entry = ""
                    if crit:
                        st.toast(f"¡CRÍTICO! 💥 {final_damage} de daño.", icon="🔥")
                        log_entry = f"🔥 CRÍTICO (D20: {damage}) -> {final_damage} Daño."
                    elif fail:
                        insult = random.choice(orc_insults)
                        st.toast(f"¡Pifia! 🤡 {insult}", icon="💩")
                        log_entry = f"💩 PIFIA (D20: 1) -> El Orco te insulta. 0 Daño."
                    else:
                        st.toast(f"¡Zas! ⚔️ {final_damage} de daño.", icon="🗡️")
                        log_entry = f"⚔️ Ataque (D20: {damage}) -> {final_damage} Daño."
                    
                    st.session_state.combat_log.insert(0, log_entry)

                    if st.session_state.monster_hp <= 0:
                        st.session_state.dungeon_stage = 'loot'
                        st.balloons()
                        st.rerun()
                
                if st.session_state.combat_log:
                    st.markdown('<div class="combat-log"><strong>📜 Historial de Batalla:</strong><br>' + "<br>".join(st.session_state.combat_log[:5]) + '</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        # --- ETAPA 4: LOOT Y ACERTIJO ---
        elif st.session_state.dungeon_stage == 'loot':
            with st.container():
                st.markdown('<div class="centered-dungeon">', unsafe_allow_html=True)
                st.success("El Orco colapsa murmurando '...todo culpa de la charola ...'.")
                st.image("https://img.icons8.com/fluency/96/treasure-chest.png", width=120)
                
                st.markdown("### 📜 El Pergamino del Guardián")
                st.caption("Responde el acertijo para demostrar que eres digno:")
                
                riddle = st.text_input("Imperio hexagonal y perfecto, almaceno recursos valiosos como un campeón. Si intentas saquear mis recursos, vas a gritar y correr. ¿Qué soy?.")
                
                if st.button("Reclamar el Trono"):
                    if riddle.strip().lower() in ["panal", "un panal", "el panal", "abeja", "la abeja", "una abeja"]:
                        st.success("¡El sello se rompe!")
                        time.sleep(1)
                        st.session_state.dungeon_stage = 'unlocked'
                        st.rerun()
                    else:
                        st.error("Respuesta incorrecta. (pista: no soy un juego de mesa, bss, bss...)")
                st.markdown('</div>', unsafe_allow_html=True)