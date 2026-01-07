# ⚔️ Leaderboard: Noche de Caballeros

> **Sistema de Gamificación y Tracking de Resultados para Juegos de Mesa.**

Aplicación Full Stack diseñada para registrar partidas, analizar el rendimiento de los jugadores (Win Rate) y premiar logros mediante un sistema de ranking histórico. Construido con foco en **Integridad de Datos** y **Reproducibilidad del Entorno**.

## 🎯 Objetivos

* **Persistencia Transaccional:** Carga de partidas con integridad referencial (Sesión -> Partida -> Participantes).
* **Métricas Avanzadas:** Cálculo automático de Win Rate y premios especiales ("Cebollitas" para segundos puestos).
* **Arquitectura Robusta:** Separación clara entre Ingesta (OLTP) y Analítica (OLAP).

## 🛠️ Stack Tecnológico Moderno

* **Frontend:** [Streamlit](https://streamlit.io/)
* **Database:** PostgreSQL 15 (Dockerized)
* **ORM:** SQLAlchemy + Pandas
* **Dependency Management:** [uv](https://github.com/astral-sh/uv) (Rust-based, ultra-fast)

## 🚀 Instalación y Despliegue Local

### 1. Prerrequisitos

* **Docker Desktop** (con WSL2 en Windows).
* **uv** instalado (`pip install uv` o `curl -LsSf https://astral.sh/uv/install.sh | sh`).

### 2. Configuración del Entorno

Clona el repositorio y entra en la carpeta:

```bash
git clone https://github.com/tu-usuario/leaderboard-caballeros.git
cd leaderboard-caballeros

```

**Seguridad:** Crea un archivo `.env` en la raíz del proyecto para tus credenciales locales (este archivo es ignorado por git):

```ini
# Archivo: .env
DB_HOST=localhost
DB_PORT=5433
DB_NAME=leaderboard_db
DB_USER=admin
DB_PASSWORD=password123

```

### 3. Levantar Infraestructura (BD)

Inicia el contenedor de PostgreSQL. Esto ejecutará automáticamente los scripts de inicialización (`sql/init.sql`).

```bash
docker-compose up -d

```

### 4. Instalar Dependencias (La Magia de uv)

Este comando leerá `uv.lock` para asegurar que instales **exactamente** las mismas versiones de librerías que se usaron en desarrollo, garantizando reproducibilidad total.

```bash
uv sync

```

### 5. Ejecutar la Aplicación

Usamos el comando `uv run` para asegurar que la app se ejecute en el entorno gestionado por uv.

```bash
uv run streamlit run app/main.py

```

*Accede a la app en: `http://localhost:8501*`

---

## 📦 Gestión de Dependencias y Reproducibilidad

Este proyecto utiliza **uv** para gestionar paquetes y versiones de Python, reemplazando a `pip` y `virtualenv` por una solución unificada y determinista.

* **`pyproject.toml`**: Define las dependencias abstractas (ej. `pandas>=2.3`).
* **`uv.lock`**: (CRÍTICO) Define las versiones exactas instaladas (ej. `pandas==2.3.3`). **Este archivo asegura que el entorno de Producción sea idéntico al de Desarrollo.**

**Para agregar nuevas librerías:**

```bash
uv add nombre_libreria

```

*(Esto actualiza automáticamente tanto el toml como el lockfile).*

## 📊 Modelo de Datos

El sistema utiliza un esquema relacional normalizado (3NF):

* **Players:** Dimensiones de los jugadores.
* **Games:** Catálogo de juegos con metadatos de complejidad.
* **Sessions:** La "juntada" (Fecha, Host).
* **Matches:** La partida específica.
* **Match_Participants:** Tabla de hechos granular para calcular participaciones y rankings.

---
