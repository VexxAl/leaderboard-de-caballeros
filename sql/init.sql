-- TABLA DE JUGADORES (Con las columnas nuevas ya integradas)
CREATE TABLE IF NOT EXISTS players (
    player_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    nickname VARCHAR(50),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Nuevos campos agregados
    birth_date DATE,
    owned_games INTEGER DEFAULT 0,
    role VARCHAR(100),
    favgame_id INTEGER -- Se vincula más abajo con ALTER para evitar error circular
);

-- TABLA DE JUEGOS
CREATE TABLE IF NOT EXISTS games (
    game_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    logo VARCHAR(10) DEFAULT '🎲',
    min_players INTEGER DEFAULT 2 NOT NULL,
    max_players INTEGER DEFAULT 4 NOT NULL,
    type VARCHAR(50) NOT NULL,
    owner_id INTEGER REFERENCES players(player_id)
);

-- TABLA DE SESIONES (Juntadas)
CREATE TABLE IF NOT EXISTS sessions (
    session_id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    location VARCHAR(100),
    host_id INTEGER REFERENCES players(player_id),
    notes TEXT
);

-- TABLA DE PARTIDAS (Matches)
CREATE TABLE IF NOT EXISTS matches (
    match_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(session_id),
    game_id INTEGER REFERENCES games(game_id),
    winner_id INTEGER REFERENCES players(player_id),
    win_type VARCHAR(50) -- 'Normal', 'Clutch', 'Paliza'
);

-- TABLA DE PARTICIPANTES POR PARTIDA
CREATE TABLE IF NOT EXISTS match_participants (
    match_id INTEGER REFERENCES matches(match_id),
    player_id INTEGER REFERENCES players(player_id),
    score INTEGER, -- Puntos (si el juego tiene)
    rank INTEGER, -- 1 = Ganador, 2 = Segundo, etc.
    PRIMARY KEY (match_id, player_id)
);

-- RELACIÓN CIRCULAR (Jugador -> Juego Favorito)
-- Lo hacemos al final porque antes no existía la tabla games
ALTER TABLE players 
ADD CONSTRAINT fk_favgame 
FOREIGN KEY (favgame_id) REFERENCES games(game_id);

-- DATOS INICIALES: JUEGOS BÁSICOS
-- Usamos INSERT IGNORE o DO NOTHING para que no falle si ya existen
INSERT INTO games (name, logo, min_players, max_players, type) VALUES 
('Catan', '🐑', 3, 6, 'Principal'),
('Splendor', '💎', 2, 4, 'Casual'),
('Survive the Island', '🏝️', 2, 5, 'Principal'),
('Carcassonne', '🏰', 2, 5, 'Casual'),
('Ticket to Ride', '🚂', 2, 5, 'Principal')
ON CONFLICT (name) DO NOTHING;