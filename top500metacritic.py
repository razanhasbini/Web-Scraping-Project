from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

# Setup Selenium driver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
service = Service()
driver = webdriver.Chrome(service=service, options=chrome_options)

# Initialize data list
movie_data = []


for page in range(0, 500):
    print(f"Scraping page {page + 1}...")
    url = f"https://www.metacritic.com/browse/movies/score/metascore/all/filtered?page={page}"
    driver.get(url)
    time.sleep(2)  
    
    movies = driver.find_elements(By.CSS_SELECTOR, "div.clamp-summary-wrap")
    
    if not movies:
        print(" No movies found on page {page + 1}. Might be rate-limited or blocked.")
        continue
    
    for movie in movies:
        try:
            title = movie.find_element(By.CSS_SELECTOR, "h3").text.strip()
        except:
            title = ""
        try:
            year = movie.find_element(By.CSS_SELECTOR, "div.clamp-details span").text.strip()
            year = year.split()[-1].replace("(", "").replace(")", "")  # Example: (2010)
        except:
            year = ""
        try:
            score = movie.find_element(By.CSS_SELECTOR, "div.clamp-metascore div").text.strip()
        except:
            score = ""
        try:
            summary = movie.find_element(By.CSS_SELECTOR, "div.summary").text.strip()
        except:
            summary = ""
        
        movie_data.append({
            "Title": title,
            "Year": year,
            "Metascore": score,
            "Summary": summary
        })
    
    time.sleep(1)

driver.quit()


df = pd.DataFrame(movie_data)
df.to_csv("metacritictopmovies.csv", index=False)

print("✅ Total movies scraped:", len(df))
print("✅ Saved to metacritictopmovies.csv")
