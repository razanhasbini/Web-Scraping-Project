import pandas as pd

# Load top movies
top_df = pd.read_csv("master_movies_final.csv")
top_df["TopMovie"] = 1

# Load lower-rated movies
low_df = pd.read_csv("movie_data.csv")

# 🧼 Rename & align columns
low_df = low_df.rename(columns={
    "movie_title": "Title",
    "title_year": "Year",
    "imdb_score": "Rating",
    "genres": "Genres",
    "director_name": "Director",
    "duration": "Runtime"
})

# 👥 Combine actor columns into one
low_df["Actors"] = low_df[["actor_1_name", "actor_2_name", "actor_3_name"]].fillna("").agg(", ".join, axis=1)

# 🧹 Keep only matching columns
top_cols = ["Title", "Year", "Rating", "Genres", "Director", "Actors", "Runtime", "TopMovie"]
low_df = low_df[top_cols[:-1]]  # no 'TopMovie' yet
low_df["TopMovie"] = 0  # label for low-rated movies

# 🧠 Clean data types
low_df["Year"] = pd.to_numeric(low_df["Year"], errors="coerce")
low_df["Rating"] = pd.to_numeric(low_df["Rating"], errors="coerce")
low_df["Runtime"] = pd.to_numeric(low_df["Runtime"], errors="coerce")

# 📦 Drop rows with missing essentials
low_df = low_df.dropna(subset=["Title", "Year", "Rating", "Runtime"])

# Combine top and low-rated
merged_df = pd.concat([top_df[top_cols], low_df], ignore_index=True)

# Save to new file
merged_df.to_csv("movies_with_labels.csv", index=False)
print("✅ Merged dataset saved as 'movies_with_labels.csv' with shape:", merged_df.shape)
