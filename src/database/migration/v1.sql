CREATE TABLE "movie" (
  "movieId" INTEGER PRIMARY KEY,  
  "imdbId" INTEGER NULL,
  "tmdbId" REAL NULL,
  "title" TEXT NULL,
  "genres" TEXT NULL
);


CREATE TABLE "tag" (
  "tagId" INTEGER PRIMARY KEY,  
  "tag" TEXT NULL
);


CREATE TABLE "movie_tags" (
  "movieId" INTEGER,  
  "tagId" INTEGER,    
  "relevance" REAL NULL,
  PRIMARY KEY ("movieId", "tagId"),  
  FOREIGN KEY ("movieId") REFERENCES "movie" ("movieId") ON DELETE CASCADE,
  FOREIGN KEY ("tagId") REFERENCES "tag" ("tagId") ON DELETE CASCADE
);


CREATE TABLE "movie_user_tag" (
  "userId" INTEGER,
  "movieId" INTEGER,  
  "tag" TEXT NULL,
  "timestamp" INTEGER NULL,
  PRIMARY KEY ("userId", "movieId"),  
  FOREIGN KEY ("movieId") REFERENCES "movie" ("movieId") ON DELETE CASCADE
);


CREATE TABLE "movie_user_rating" (
  "userId" INTEGER,
  "movieId" INTEGER,  
  "rating" REAL  NULL,
  "timestamp" INTEGER NULL,
  PRIMARY KEY ("userId", "movieId"), 
  FOREIGN KEY ("movieId") REFERENCES "movie" ("movieId") ON DELETE CASCADE
);
