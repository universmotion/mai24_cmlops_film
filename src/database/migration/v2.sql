CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE "movies" (
  "movieId" INTEGER PRIMARY KEY,  
  "title" VARCHAR NULL,
  "genres" VARCHAR NULL
);


CREATE TABLE "users" (
  "userId" SERIAL PRIMARY KEY,  
  "count_movies" INTEGER DEFAULT 0,
  "no_genres_listed" REAL DEFAULT 0,
  "Action" REAL DEFAULT 0,
  "Adventure" REAL DEFAULT 0,
  "Animation" REAL DEFAULT 0,
  "Children" REAL DEFAULT 0,
  "Comedy" REAL DEFAULT 0,
  "Crime" REAL DEFAULT 0,
  "Documentary" REAL DEFAULT 0,
  "Drama" REAL DEFAULT 0,
  "Fantasy" REAL DEFAULT 0,
  "Film_Noir" REAL DEFAULT 0,
  "Horror" REAL DEFAULT 0,
  "IMAX" REAL DEFAULT 0,
  "Musical" REAL DEFAULT 0,
  "Mystery" REAL DEFAULT 0,
  "Romance" REAL DEFAULT 0,
  "Sci_Fi" REAL DEFAULT 0,
  "Thriller" REAL DEFAULT 0,
  "War" REAL DEFAULT 0,
  "Western" REAL DEFAULT 0
);

CREATE TABLE "movies_users_rating" (
  "userId" INTEGER,
  "movieId" INTEGER,  
  "rating" REAL  NULL,
  "timestamp" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "is_recommended" BOOLEAN DEFAULT FALSE,
  "is_use_to_train" BOOLEAN DEFAULT FALSE,
  PRIMARY KEY ("userId", "movieId"), 
  FOREIGN KEY ("movieId") REFERENCES "movies" ("movieId") ON DELETE cascade,
  FOREIGN KEY ("userId") REFERENCES "users" ("userId") ON DELETE CASCADE
);

CREATE TABLE clients (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(), 
    "username" VARCHAR(255) UNIQUE NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "email" VARCHAR(255) UNIQUE NOT NULL,
    "hashed_password" VARCHAR(255) NOT NULL
);