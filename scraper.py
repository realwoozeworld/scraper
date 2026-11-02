import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "https://www.conrad.de"
SEARCH_URL = f"{BASE_URL}/de/search.html?search=balluff%20induktiver%20sensor"

def main():
    # Initialize Selenium Chrome
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    print("Launching browser...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    
    print("\n" + "="*60)
    print("MANUAL ACTION REQUIRED:")
    print("1. A browser window has opened.")
    print("2. Accept cookies and manually log in to your Conrad.de account.")
    print("3. Once you are successfully logged in, come back here.")
    print("="*60 + "\n")
    
    driver.get(BASE_URL)
    input(">>> PRESS 'ENTER' HERE ONLY AFTER YOU HAVE LOGGED IN TO CONTINUE SCRIPT <<<")
    
    print("\nNavigating to search page...")
    driver.get(SEARCH_URL)
    
    links = set()
    max_items = 100
    
    print("Collecting product links...")
    while len(links) < max_items:
        time.sleep(2)
        elements = driver.find_elements(By.CSS_SELECTOR,'a[href*="/de/p/"]')
        for el in elements:
            href = el.get_attribute("href")
            if href:
                if href.startswith("http"):
                    links.add(href)
                else:
                    links.add(BASE_URL + href)
            if len(links) >= max_items:
                break
        
        # Try to go to next page
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, 'a.pagination__next, button[class*="next"]')
            next_btn.click()
        except:
            print("No more pages available or pagination button not found.")
            break
            
    product_links = list(links)[:max_items]
    all_data = []
    print(f"Found {len(product_links)} product links. Starting to extract data...")
    
    for i, url in enumerate(product_links, 1):
        print(f"Scraping product {i}/{len(product_links)}: {url}")
        driver.get(url)
        time.sleep(2)
        
        data = {"URL": url}
        try:
            data["Breadcrumbs"] = driver.find_element(By.CSS_SELECTOR, '.breadcrumb, [aria-label="Breadcrumb"]').text.replace('\n', ' > ')
        except:
            data["Breadcrumbs"] = None

        try:
            data["Product_Name"] = driver.find_element(By.TAG_NAME, 'h1').text
        except:
            data["Product_Name"] = None
            
        try:
            data["Price"] = driver.find_element(By.CSS_SELECTOR, '.product-price, [class*="Price"]').text
        except:
            data["Price"] = None
            
        try:
            data["Image_URL"] = driver.find_element(By.CSS_SELECTOR, '.product-image img, [class*="gallery"] img').get_attribute("src")
        except:
            data["Image_URL"] = None
        
        try:
            data["Highlights"] = driver.find_element(By.CSS_SELECTOR, '#highlights-details, [class*="highlights"]').text
        except:
            data["Highlights"] = None
        
        try:
            tech_data = {}
            rows = driver.find_elements(By.CSS_SELECTOR, '#technische-daten tr, table tr')
            for row in rows:
                cols = row.find_elements(By.CSS_SELECTOR, 'td, th')
                if len(cols) >= 2:
                    tech_data[cols[0].text.strip()] = cols[1].text.strip()
            data["Technical_Data"] = str(tech_data)
        except:
            data["Technical_Data"] = None
        
        try:
            doc_link = driver.find_element(By.XPATH, '//a[contains(text(), "Datenblatt")]').get_attribute("href")
            data["Datasheet_URL"] = BASE_URL + doc_link if doc_link and not doc_link.startswith("http") else doc_link
        except:
            data["Datasheet_URL"] = None
        
        try:
            data["Description"] = driver.find_element(By.CSS_SELECTOR, '#beschreibung, [class*="description"]').text
        except:
            data["Description"] = None
        
        try:
            offer_btn = driver.find_element(By.XPATH, '//button[contains(text(), "Alle Angebote")]')
            offer_btn.click()
            time.sleep(1)
            data["Other_Offers"] = driver.find_element(By.CSS_SELECTOR, '.offers-list, [class*="offers"]').text
        except:
            data["Other_Offers"] = "No other offers found"
            
        all_data.append(data)
        
    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv("conrad_balluff_products.csv", index=False, encoding='utf-8')
        print("Data successfully saved to: conrad_balluff_products.csv")
    else:
        print("No data was collected.")
        
    driver.quit()

if __name__ == "__main__":
    main()