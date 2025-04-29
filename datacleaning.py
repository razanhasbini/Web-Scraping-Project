import pandas as pd

df = pd.read_csv("master_movies_cleaned.csv")


df["Genres"] = df["Genres"].combine_first(df["Genres_x"]).combine_first(df["Genres_y"])
df["Director"] = df["Director"].combine_first(df["Director_x"]).combine_first(df["Director_y"])
df["Runtime"] = df["Runtime(min)"].combine_first(df["Runtime_x"]).combine_first(df["Runtime_y"])

df = df.drop(columns=[
    "Genres_x", "Genres_y",
    "Director_x", "Director_y",
    "Runtime(min)", "Runtime_x", "Runtime_y"
], errors="ignore")

df["Genres"] = df["Genres"].astype(str).str.lower().str.replace("|", ",").str.replace("/", ", ")
df["Director"] = df["Director"].astype(str).str.strip().str.lower().str.title()


df.to_csv("master_movies_final.csv", index=False)
print("✅ Final dataset saved as 'master_movies_final.csv' — ready for analysis!")
