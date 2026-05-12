CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =========================
-- TABLE USER
-- =========================

CREATE TABLE "user" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- TABLE HARDWARE
-- =========================

CREATE TABLE hardware (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL,

    name VARCHAR(255),
    cpu VARCHAR(255),
    gpu VARCHAR(255),
    gb_ram INTEGER,
    storage_type VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_hardware_user
        FOREIGN KEY(user_id)
        REFERENCES "user"(id)
        ON DELETE CASCADE
);

-- =========================
-- TABLE VIDEOGAME
-- =========================

CREATE TABLE videogame (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(255) NOT NULL,
    genre VARCHAR(100),
    developer VARCHAR(255),
    release_year INTEGER
);

-- =========================
-- TABLE VIDEOGAME_REQUIREMENT
-- =========================

CREATE TABLE videogame_requirement (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    videogame_id UUID NOT NULL,

    requirement_level VARCHAR(50),

    cpu VARCHAR(255),
    gpu VARCHAR(255),

    gb_ram INTEGER,
    target_fps INTEGER,

    resolution VARCHAR(50),
    settings VARCHAR(100),

    CONSTRAINT fk_requirement_game
        FOREIGN KEY(videogame_id)
        REFERENCES videogame(id)
        ON DELETE CASCADE
);

-- =========================
-- TABLE RESULT
-- =========================

CREATE TABLE result (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    hardware_id UUID NOT NULL,

    benchmark_type VARCHAR(100),

    score FLOAT NOT NULL,

    fps_avg FLOAT,
    fps_min INTEGER,
    fps_max INTEGER,

    resolution VARCHAR(50),
    settings VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_result_hardware
        FOREIGN KEY(hardware_id)
        REFERENCES hardware(id)
        ON DELETE CASCADE
);

-- =========================
-- TABLE GAME_RESULT
-- =========================

CREATE TABLE game_result (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    hardware_id UUID NOT NULL,
    videogame_id UUID NOT NULL,

    fps_avg FLOAT,
    fps_min INTEGER,
    fps_max INTEGER,

    resolution VARCHAR(50),
    settings VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_game_result_hardware
        FOREIGN KEY(hardware_id)
        REFERENCES hardware(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_game_result_game
        FOREIGN KEY(videogame_id)
        REFERENCES videogame(id)
        ON DELETE CASCADE
);