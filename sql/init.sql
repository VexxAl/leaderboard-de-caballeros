-- Crea las tablas si no existen

-- 1. Jugadores
CREATE TABLE IF NOT EXISTS players (
    player_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    nickname VARCHAR(50),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Catálogo de Juegos
CREATE TABLE IF NOT EXISTS games (
    game_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50),
    complexity_weight DECIMAL(3,2), -- De 1.00 a 5.00
    img_url VARCHAR(255)
);

-- 3. Sesiones (Juntadas)
CREATE TABLE IF NOT EXISTS sessions (
    session_id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    location VARCHAR(100),
    host_id INT REFERENCES players(player_id),
    notes TEXT
);

-- 4. Partidas (Matches)
CREATE TABLE IF NOT EXISTS matches (
    match_id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(session_id),
    game_id INT REFERENCES games(game_id),
    winner_id INT REFERENCES players(player_id),
    win_type VARCHAR(50) -- 'Paliza', 'Clutch', 'Normal'
);

-- 5. Participantes por Partida (Detalle)
CREATE TABLE IF NOT EXISTS match_participants (
    match_id INT REFERENCES matches(match_id),
    player_id INT REFERENCES players(player_id),
    score INT,
    rank INT, -- 1=Ganador, 2=Segundo...
    PRIMARY KEY (match_id, player_id)
);

-- SEED DATA (Datos de prueba iniciales)
INSERT INTO players (name, nickname) VALUES 
('Yo', 'Admin'),
('Agu', 'El Suertudo'),
('Mati', 'El Estratega')
ON CONFLICT DO NOTHING;

INSERT INTO games (name, category, complexity_weight) VALUES 
('Catan', 'Estrategia', 2.3),
('TEG', 'Guerra', 3.0),
('Uno', 'Party', 1.1)
ON CONFLICT DO NOTHING;