-- Création des tables avec clés primaires et étrangères

-- Table movie
CREATE TABLE "movie" (
  "movieId" INTEGER PRIMARY KEY,  -- Clé primaire
  "imdbId" INTEGER,
  "tmdbId" REAL,
  "title" TEXT,
  "genres" TEXT
);

-- Table tag
CREATE TABLE "tag" (
  "tagId" INTEGER PRIMARY KEY,  -- Clé primaire
  "tag" TEXT
);

-- Table movie_tag
CREATE TABLE "movie_tags" (
  "movieId" INTEGER,  -- Clé étrangère vers movie
  "tagId" INTEGER,    -- Clé étrangère vers tag
  "relevance" REAL,
  PRIMARY KEY ("movieId", "tagId"),  -- Clé primaire composite
  FOREIGN KEY ("movieId") REFERENCES "movie" ("movieId") ON DELETE CASCADE,
  FOREIGN KEY ("tagId") REFERENCES "tag" ("tagId") ON DELETE CASCADE
);

-- Table movie_user_tag
CREATE TABLE "movie_user_tag" (
  "userId" INTEGER,
  "movieId" INTEGER,  -- Clé étrangère vers movie
  "tag" TEXT,
  "timestamp" INTEGER,
  PRIMARY KEY ("userId", "movieId", "tag"),  -- Clé primaire composite
  FOREIGN KEY ("movieId") REFERENCES "movie" ("movieId") ON DELETE CASCADE
);

-- Table movie_user_rating
CREATE TABLE "movie_user_rating" (
  "userId" INTEGER,
  "movieId" INTEGER,  -- Clé étrangère vers movie
  "rating" REAL,
  "timestamp" INTEGER,
  PRIMARY KEY ("userId", "movieId"),  -- Clé primaire composite
  FOREIGN KEY ("movieId") REFERENCES "movie" ("movieId") ON DELETE CASCADE
);
