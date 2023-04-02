-- Создание базы онлайн-кинотеатра:
CREATE DATABASE movies_database;

-- Создание отдельной схемы для контента:
CREATE SCHEMA IF NOT EXISTS content;

-- Информация о фильмах:
CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    rating FLOAT,
    type TEXT NOT NULL,
    created TIMESTAMP WITH TIME ZONE,
    modified TIMESTAMP WITH TIME ZONE
);

-- Список жанров:
CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created TIMESTAMP WITH TIME ZONE,
    modified TIMESTAMP WITH TIME ZONE
);

-- Актеры и участники съемок:
CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name TEXT NOT NULL,
    created TIMESTAMP WITH TIME ZONE,
    modified TIMESTAMP WITH TIME ZONE
);

-- Жанры кинопроизведений:
CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    CONSTRAINT fk_genre_id
      FOREIGN KEY(id)
      REFERENCES genre(id)
      ON DELETE CASCADE
      ON UPDATE CASCADE,
    CONSTRAINT fk_film_work_id
      FOREIGN KEY(id)
      REFERENCES film_work(id)
      ON DELETE CASCADE
      ON UPDATE CASCADE,
    created TIMESTAMP WITH TIME ZONE
);

-- Люди, принимавшие участие в создании кинопроизведения:
CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    CONSTRAINT fk_person_id
      FOREIGN KEY(id)
      REFERENCES person(id)
      ON DELETE CASCADE
      ON UPDATE CASCADE,
    CONSTRAINT fk_film_work_id
      FOREIGN KEY(id)
      REFERENCES film_work(id)
      ON DELETE CASCADE
      ON UPDATE CASCADE,
    role TEXT NOT NULL,
    created TIMESTAMP WITH TIME ZONE
);

-- Индекс для оптимизации запросов по дате выхода и рейтингу:
CREATE INDEX creation_date_rating_idx ON content.film_work
    (creation_date, rating);

-- Уникальный индекс для фильмов и актеров:
CREATE UNIQUE INDEX film_work_person_idx ON content.person_film_work
    (fk_film_work_id, fk_person_id);

-- Уникальный индекс для фильмов по жанру:
CREATE UNIQUE INDEX genre_film_work_idx ON content.genre_film_work
    (fk_genre_id, fk_film_work_id);



CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    genre_id uuid NOT NULL,
    film_work_id uuid NOT NULL,
    created timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    person_id uuid NOT NULL,
    role TEXT NOT NULL,
    created timestamp with time zone
);
