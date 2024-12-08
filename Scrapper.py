from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import random

# Function to set up Selenium WebDriver
def setup_driver():
    options = Options()
    options.add_argument('--headless')  # Run in headless mode (no browser UI)
    options.add_argument('--disable-gpu')  # Disable GPU rendering
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('log-level=3')  # Suppress logs

    # Path to the chromedriver (update this to your correct path)
    service = Service("../chromedriver-mac-arm64/chromedriver")  # Path to ChromeDriver
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Function to wait for elements
def wait_for_element(driver, locator, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, locator))
        )
        return element
    except Exception as e:
        print(f"Error waiting for element: {e}")
        return None

# Scroll the page down to load more products
def scroll_to_bottom(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# Function to scrape a single page
def scrape_flipkart_page(driver, url):
    driver.get(url)
    time.sleep(random.uniform(3, 5))  # Increase wait for page load
    scroll_to_bottom(driver)  # Scroll down to load all products

    # Wait for the product containers to load (use XPath instead of class name)
    product_locator = "//div[@class='_75nlfW']"  # XPath for the product container
    products = wait_for_element(driver, product_locator, timeout=15)

    if products:
        product_data = []
        # Find all product elements using XPath
        product_elements = driver.find_elements(By.XPATH, "//div[@class='_1sdMkc LFEi7Z']")

        for product in product_elements:
            try:
                name = product.find_element(By.XPATH, ".//a[@class='WKTcLC']").text
            except:
                name = None

            try:
                price = product.find_element(By.XPATH, ".//div[@class='Nx9bqj']").text.replace('₹', '').replace(',', '')
            except:
                price = None

            try:
                discount = product.find_element(By.XPATH, ".//div[@class='UkUFwK']").text
            except:
                discount = None

            product_data.append({
                'Product Name': name,
                'Price (₹)': price,
                'Discount': discount,
            })
        
        print(f"Found {len(product_data)} products on this page.")
        return product_data
    else:
        print("No products found.")
        return []

# Main function to scrape multiple pages
def scrape_flipkart(base_url, max_pages=5):
    driver = setup_driver()
    all_products = []

    for page in range(1, max_pages + 1):
        print(f"Scraping page {page}...")
        url = f"{base_url}&page={page}"
        products = scrape_flipkart_page(driver, url)
        if not products:
            break
        all_products.extend(products)

    driver.quit()  # Close the driver after scraping
    return all_products

# URL of the Flipkart category to scrape
base_url = "https://www.flipkart.com/clothing-and-accessories/saree-and-accessories/saree/women-saree/pr?sid=clo%2C8on%2Czpd%2C9og&otracker=categorytree&otracker=nmenu_sub_Women_0_Sarees"

# Start scraping
print("Starting data scraping...")
data = scrape_flipkart(base_url, max_pages=5)
print(f"Scraped {len(data)} products.")

# Save data to CSV and Excel
if data:
    df = pd.DataFrame(data)
    df.to_csv('flipkart_data.csv', index=False)
    df.to_excel('flipkart_data.xlsx', index=False)
    print("Data saved to flipkart_data.csv and flipkart_data.xlsx")
else:
    print("No data scraped.")
