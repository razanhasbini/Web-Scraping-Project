from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from textblob import TextBlob
import streamlit as st
import pandas as pd
import numpy as np
import re

st.set_page_config(page_title=" Movie Explorer + ML Predictor", layout="wide")


df = pd.read_csv("master_movies_final.csv")
label_df = pd.read_csv("movies_with_labels.csv")

# Clean data
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df = df.dropna(subset=["Year"])
df["Year"] = df["Year"].astype(int)
df["Genres"] = df["Genres"].astype(str)
df["Director"] = df["Director"].astype(str)
df["Actors"] = df["Actors"].astype(str)
df["Title"] = df["Title"].astype(str)
df["Overview"] = df["Overview"].fillna("").astype(str)

@st.cache_data
def compute_sentiment(df):
    df["Sentiment"] = df["Overview"].apply(lambda x: TextBlob(x).sentiment.polarity)
    return df

df = compute_sentiment(df)

st.sidebar.header("📊 Filter Movies")
search_title = st.text_input("🔍 Search by Movie Title")
min_year, max_year = df["Year"].min(), df["Year"].max()
year_range = st.sidebar.slider("Year Range", int(min_year), int(max_year), (2000, 2025))

genre_series = df["Genres"].dropna().astype(str)
split_genres = genre_series.apply(lambda x: re.split(r'[|,]', x))
flat_genres = [g.strip().title() for sublist in split_genres for g in sublist if g.strip()]
genres = sorted(set(flat_genres))
directors = sorted(df["Director"].dropna().unique().tolist())

selected_genre = st.sidebar.selectbox("Genre", ["All"] + genres)
selected_director = st.sidebar.selectbox("Director", ["All"] + directors[:100])

filtered_df = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]
if selected_genre != "All":
    filtered_df = filtered_df[filtered_df["Genres"].str.contains(selected_genre, case=False)]
if selected_director != "All":
    filtered_df = filtered_df[filtered_df["Director"] == selected_director]
if search_title:
    filtered_df = filtered_df[filtered_df["Title"].str.contains(search_title, case=False)]

st.subheader(f"🎥 Showing {len(filtered_df)} Movies")
st.dataframe(filtered_df[["Title", "Year", "Genres", "Director", "Rating", "RT_CriticScore", "Metascore"]])

st.markdown("### 📈 Score Comparison")
score_cols = ['Rating', 'RT_CriticScore', 'Metascore']
available_scores = [col for col in score_cols if col in filtered_df.columns]
if len(available_scores) >= 2:
    selected_scores = st.multiselect("Select Scores to Compare", available_scores, default=available_scores)
    st.line_chart(filtered_df[selected_scores])

st.markdown("### Top Genres")
all_filtered_genres = filtered_df["Genres"].dropna().astype(str)
split_filtered = all_filtered_genres.apply(lambda x: re.split(r'[|,]', x))
flat_filtered = [g.strip().title() for sublist in split_filtered for g in sublist if g.strip()]
genre_counts = pd.Series(flat_filtered).value_counts().head(10)
st.bar_chart(genre_counts)

st.markdown("### Average Sentiment by Genre")
df['PrimaryGenre'] = df['Genres'].apply(lambda x: re.split(r'[|,]', str(x))[0].strip().title() if pd.notna(x) else "Unknown")
avg_sentiment = df.groupby("PrimaryGenre")["Sentiment"].mean().sort_values(ascending=False).head(10)
st.bar_chart(avg_sentiment)


label_df = label_df.dropna(subset=["Year", "Runtime", "Genres", "Director", "Actors", "Rating"])
label_df["TopMovie"] = label_df["TopMovie"].astype(int)
label_df = label_df[~label_df["Director"].str.lower().str.contains("leone")]
label_df["Sentiment"] = label_df["Title"].apply(lambda x: TextBlob(str(x)).sentiment.polarity)


def compute_actor_score(actor_str, df):
    actors = [a.strip() for a in actor_str.split(',') if a.strip() != ""]
    scores = []
    for actor in actors:
        score = df[df["Actors"].str.contains(actor, case=False, na=False)]["TopMovie"].mean()
        if not np.isnan(score):
            scores.append(score)
    return np.mean(scores) if scores else 0

label_df["ActorAvg"] = label_df["Actors"].apply(lambda x: compute_actor_score(x, label_df))
label_df["DirectorFreq"] = label_df.groupby("Director")["TopMovie"].transform("mean")
label_df["OverviewLength"] = label_df["Title"].apply(lambda x: len(str(x)))

features = ["Year", "Runtime", "Genres", "Director", "Sentiment", "DirectorFreq", "ActorAvg", "OverviewLength"]
X_class = label_df[features]
y_class = label_df["TopMovie"]
y_reg = label_df["Rating"]

cat_features = ["Genres", "Director"]
preprocessor = ColumnTransformer([
    ('cat', OneHotEncoder(handle_unknown="ignore", sparse=False), cat_features)
], remainder='passthrough')

clf_model = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression(max_iter=1000, random_state=42))
])

reg_model = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', LinearRegression())
])

X_train_class, _, y_train_class, _ = train_test_split(X_class, y_class, stratify=y_class, test_size=0.2, random_state=42)
X_train_reg, _, y_train_reg, _ = train_test_split(X_class, y_reg, test_size=0.2, random_state=42)

clf_model.fit(X_train_class, y_train_class)
reg_model.fit(X_train_reg, y_train_reg)

st.markdown("### Enter New Movie Info to Predict Top Movie Status and Rating")

col1, col2 = st.columns(2)
year = col1.number_input("Release Year", 2025, 2035, 2025)
runtime = col2.number_input("Runtime (minutes)", 60, 240, 120)

genre_series = label_df["Genres"].dropna().astype(str)
split_genres = genre_series.apply(lambda x: re.split(r'[|,]', x))
flat_genres = [g.strip().title() for sublist in split_genres for g in sublist if g.strip()]
genre_options = sorted(set(flat_genres))

genre = st.selectbox("Genre", genre_options)
director = st.text_input("Director", "Christopher Nolan")
actors = st.text_input("Main Actors (comma separated)", "Leonardo DiCaprio, Joseph Gordon-Levitt")
overview = st.text_area("Movie Overview", "A thrilling tale of adventure and survival in a post-apocalyptic world.")

if st.button("🚀 Predict"):
    sentiment = TextBlob(overview).sentiment.polarity
    director_freq = label_df[label_df["Director"] == director]["TopMovie"].mean()
    director_freq = 0 if np.isnan(director_freq) else director_freq
    actor_avg = compute_actor_score(actors, label_df)
    overview_len = len(overview)

    input_df = pd.DataFrame([{
        "Year": year,
        "Runtime": runtime,
        "Genres": genre,
        "Director": director,
        "Sentiment": sentiment,
        "DirectorFreq": director_freq,
        "ActorAvg": actor_avg,
        "OverviewLength": overview_len
    }])

    top_pred = clf_model.predict(input_df)[0]
    top_prob = clf_model.predict_proba(input_df)[0][1]
    rating_pred = reg_model.predict(input_df)[0]

    st.info("⚠️ Predictions are based on past patterns, not real-time popularity.")

    if top_pred == 1:
        st.success(f" Top Movie: Yes ({top_prob*100:.2f}% probability)")
    else:
        st.warning(f" Top Movie: No ({top_prob*100:.2f}% probability)")

    st.markdown(f"### Predicted IMDb Rating: **{rating_pred:.2f} / 10**")