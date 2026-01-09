import streamlit as st

st.set_page_config(page_title="Reglamento", page_icon="📜", layout="centered")

if st.button("⬅️ Volver al Tablero"):
    st.switch_page("main.py")
    
st.title("📜 El Código de los Caballeros")
st.caption("Normas vigentes aprobadas por la Mesa Chica para el ciclo 2026.")

st.divider()

# --- SECCIÓN 1: LAS NUEVAS REGLAS (2026) ---
st.header("⚖️ La Nueva Constitución (2026)")

st.info("📢 **SISTEMA DE PREMIOS Y CASTIGOS**")

st.markdown("""
* **🏆 La Meta de los 5:** Todo jugador que alcance las **5 victorias** en cualquier juego será galardonado.
* **🍷 El Tributo:** El premio (Vino o similar) será costeado por los otros 5 jugadores (**2 USD c/u**).
* **📈 Plusvalía Histórica:** Ganar el premio suma **+1 PV** en el registro histórico vitalicio.
* **🚫 Exclusión de Pago:** Si durante la sumatoria de esas 5 victorias, un jugador **no participó nunca**, queda exento de poner plata para el premio.
* **🤝 Ley de Delegación:** En caso de no poder asistir, se permite delegar a un **reemplazo** la potestad de jugar (y ganar) en su nombre.
""")


st.divider()

# --- SECCIÓN 2: REGLAS DE CONVIVENCIA ---
st.header("🛡️ Los Mandamientos Ancestrales")
st.caption("Reglas de etiqueta y honor que rigen desde tiempos inmemoriales.")

col1, col2 = st.columns(2)

with col1:
    st.success("**LO QUE SÍ**")
    st.markdown("""
    * **Juego Dinámico:** Prioridad absoluta. Soft game de entrada, picante después.
    * **Horario Prudente:** Retorno a los hogares a horas razonables.
    * **Delivery/Aportes:** La comida se gestiona entre todos.
    * **Chascarrillos:** Todo puede (y debe) ser tomado con humor.
    """)

with col2:
    st.error("**LO QUE NO**")
    st.markdown("""
    * **Manos Sucias:** Prohibido tocar componentes con grasa.
    * **Llantos:** Menos quejas, más tirar dados.
    * **Exclusión:** Nadie queda fuera, puede haber espera pero se juega.
    """)

# Footer
st.markdown("---")
st.caption("🏛️ *Dura Lex, Sed Lex* (La ley es dura, pero es la ley).")