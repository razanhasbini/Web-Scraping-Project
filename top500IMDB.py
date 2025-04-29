from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

# Setup Selenium driver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no browser UI)
service = Service()  # Automatically find chromedriver
driver = webdriver.Chrome(service=service, options=chrome_options)

# Initialize list
movie_data = []

# Visit top-rated movies page
base_url = "https://www.themoviedb.org/movie/top-rated?page="

for page in range(1, 26):  # 25 pages
    print(f"Scraping page {page}...")
    driver.get(base_url + str(page))
    time.sleep(2)  # Give page time to load

    movies = driver.find_elements(By.CSS_SELECTOR, "div.card.style_1")

    for movie_card in movies:
        title_element = movie_card.find_element(By.CSS_SELECTOR, "h2 a")
        title = title_element.text
        link = title_element.get_attribute("href")

        # Visit movie detail page
        driver.get(link)
        time.sleep(2)

        try:
            year = driver.find_element(By.CSS_SELECTOR, "span.release_date").text.strip("()").split("-")[0]
        except:
            year = ""

        try:
            rating = driver.find_element(By.CSS_SELECTOR, "div.user_score_chart").get_attribute("data-percent")
            rating = float(rating) / 10  # TMDB scores are x10
        except:
            rating = ""

        try:
            votes = driver.find_element(By.XPATH, "//span[contains(text(),'User Score')]/following-sibling::span").text
        except:
            votes = ""

        try:
            overview = driver.find_element(By.CSS_SELECTOR, "div.header_info p").text
        except:
            overview = ""

        try:
            runtime = driver.find_element(By.XPATH, "//span[contains(text(),'Runtime')]/following-sibling::span").text
            runtime = runtime.split()[0]  # e.g., "148 minutes" -> "148"
        except:
            runtime = ""

        try:
            genres = driver.find_element(By.CSS_SELECTOR, "span.genres").text
        except:
            genres = ""

    
        director = ""
        actors = []

        try:
            people_sections = driver.find_elements(By.CSS_SELECTOR, "ol.people.scroller li.profile")
            for person in people_sections:
                job = person.find_element(By.CSS_SELECTOR, "p.character").text
                name = person.find_element(By.CSS_SELECTOR, "p a").text
                if "Director" in job and director == "":
                    director = name
                if "Actor" in job or "Actress" in job:
                    if len(actors) < 5:
                        actors.append(name)
        except:
            pass

        movie_data.append({
            "Title": title,
            "Year": year,
            "Rating": rating,
            "Votes": votes,
            "Runtime(min)": runtime,
            "Genres": genres,
            "Overview": overview,
            "Director": director,
            "Actors": ", ".join(actors)
        })

        driver.back()
        time.sleep(1)

driver.quit()

df = pd.DataFrame(movie_data)
df.to_csv("tmdb_top_500_movies_scraped.csv", index=False)

print("✅ Total movies scraped:", len(df))
print("✅ Saved to tmdb_top_500_movies_scraped.csv")
