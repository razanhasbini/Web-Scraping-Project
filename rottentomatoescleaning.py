from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

chrome_options = Options()
chrome_options.add_argument("--headless")  
service = Service()
driver = webdriver.Chrome(service=service, options=chrome_options)


movie_data = []

base_url = "https://www.rottentomatoes.com/top/bestofrt/"

driver.get(base_url)
time.sleep(3)


movies = driver.find_elements(By.CSS_SELECTOR, "table.table a.unstyled.articleLink")

movie_links = [m.get_attribute("href") for m in movies]

print(f"Found {len(movie_links)} movies")

for idx, link in enumerate(movie_links):
    print(f"Scraping movie {idx + 1}: {link}")
    driver.get(link)
    time.sleep(2)
    
    try:
        title = driver.find_element(By.CSS_SELECTOR, "h1.scoreboard__title").text
    except:
        title = ""
    
    try:
        critic_score = driver.find_element(By.CSS_SELECTOR, "score-board").get_attribute("tomatometerscore")
    except:
        critic_score = ""
    
    try:
        people_score = driver.find_element(By.CSS_SELECTOR, "score-board").get_attribute("audiencescore")
    except:
        people_score = ""
    
    try:
        genre = driver.find_element(By.XPATH, "//div[@data-qa='movie-info-item-value' and preceding-sibling::div[text()='Genre:']]").text
    except:
        genre = ""
    
    try:
        director = driver.find_element(By.XPATH, "//div[@data-qa='movie-info-item-value' and preceding-sibling::div[text()='Director:']]").text
    except:
        director = ""
    
    try:
        runtime = driver.find_element(By.XPATH, "//div[@data-qa='movie-info-item-value' and preceding-sibling::div[text()='Runtime:']]").text
    except:
        runtime = ""
    
    try:
        release_date = driver.find_element(By.XPATH, "//div[@data-qa='movie-info-item-value' and preceding-sibling::div[text()='Release Date (Theaters):']]").text
    except:
        release_date = ""
    
    movie_data.append({
        "Title": title,
        "CriticScore": critic_score,
        "AudienceScore": people_score,
        "Genres": genre,
        "Director": director,
        "Runtime": runtime,
        "ReleaseDate": release_date,
        "Link": link
    })
    
    time.sleep(1) 

driver.quit()


df = pd.DataFrame(movie_data)
df.to_csv("rottentomatoes_topmovies.csv", index=False)

print(" Done! Saved to rottentomatoes_topmovies.csv")
