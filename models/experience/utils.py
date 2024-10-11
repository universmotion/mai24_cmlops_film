# apply function
def group_set(df):
    list_dico = df[["movieId", "rating"]].to_dict(orient="records")
    return {d["movieId"]: d["rating"] for d in list_dico}


def multi_with_rating(df):
    return (df["rating"]) * df.drop(["userId", "movieId", "rating"])


def put_rating(df, dico):
    if df["userId"] in dico.index:
        rating_done = dico.loc[df["userId"]]
        movies_recommanded = df.drop(["userId"])
        list_of_recommended_movie_with_rating_test = [
            rating_done[movieId]
            for movieId in movies_recommanded.values
            if movieId in list(rating_done.keys())
        ]
    return list_of_recommended_movie_with_rating_test
