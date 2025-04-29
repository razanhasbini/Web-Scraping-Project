import pandas as pd

tmdb = pd.read_csv(".venv/tmdb_top_500_movies.csv")
rt = pd.read_csv(".venv/rottentomatoes_top500_clean.csv")
meta = pd.read_csv(".venv/metacritic_top500_clean.csv")


# Normalize title + year for all datasets
def clean_title_year(df, title_col="Title", year_col="Year"):
    df[title_col] = df[title_col].astype(str).str.lower().str.strip()
    df[year_col] = df[year_col].astype(str).str.extract(r'(\d{4})')  # extract only year
    return df

tmdb = clean_title_year(tmdb)
rt = clean_title_year(rt)
meta = clean_title_year(meta)


merged = pd.merge(tmdb, rt, on=["Title", "Year"], how="outer")


final = pd.merge(merged, meta, on=["Title", "Year"], how="outer")


final.to_csv("master_movies_dataset.csv", index=False)
print(" Final dataset created:", final.shape)
