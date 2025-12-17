import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def make_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=opts)
    return driver

def scrape_jurisprudence():
    driver = make_driver()
    wait = WebDriverWait(driver, 30)
    
    try:
        print("Apertura banca dati giurisprudenza...")
        driver.get("https://bancadatigiurisprudenza.giustiziatributaria.gov.it/ricerca")
        time.sleep(2)  # Wait for page to fully load
        
        print("Selezione anno...")
        # Select year 2025 using ID selector
        anno_select = wait.until(EC.presence_of_element_located(
            (By.ID, "Form.ControlInput2")
        ))
        Select(anno_select).select_by_value("2025")
        time.sleep(1)
        
        print("Selezione esito favorevole...")
        # Select favorable outcome using ID selector
        esito_select = wait.until(EC.presence_of_element_located(
            (By.ID, "Form.ControlInput9")
        ))
        Select(esito_select).select_by_visible_text("Favorevole al contribuente")
        time.sleep(1)
        
        print("Avvio ricerca...")
        # Click search button
        ricerca_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(),'Ricerca')]")
        ))
        ricerca_btn.click()
        time.sleep(3)  # Wait for results to load
        
        print("Attesa risultati...")
        # Wait for results table to appear
        wait.until(EC.presence_of_element_located((By.XPATH, "//table")))
        time.sleep(2)
        
        print("Apertura prima sentenza...")
        # Click on first result link
        first_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "(//a[contains(@href,'dettaglio')])[1]")
        ))
        first_link.click()
        time.sleep(3)  # Wait for detail page to load
        
        print("Estrazione testo...")
        # Extract text from the detail page
        text_block = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class,'sentenza') or contains(@class,'container') or contains(@class,'content')]")
        ))
        
        testo = text_block.text
        if not testo or len(testo.strip()) < 100:
            # Try alternative selectors
            testo = driver.find_element(By.TAG_NAME, "body").text
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "testo": testo,
            "status": "success"
        }
        
        os.makedirs("data", exist_ok=True)
        with open("data/sentenza_oggi.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        with open("data/sentenza_oggi.txt", "w", encoding="utf-8") as f:
            f.write(testo)
        
        print("Salvataggio completato!")
        return True
        
    except TimeoutException as e:
        print(f"Errore: Timeout nell'attesa elemento - {str(e)}")
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error_type": "TimeoutException",
            "error": str(e),
            "current_url": driver.current_url
        }
        os.makedirs("data", exist_ok=True)
        with open("data/sentenza_oggi.json", "w", encoding="utf-8") as f:
            json.dump(error_data, f, ensure_ascii=False, indent=2)
        return False
        
    except NoSuchElementException as e:
        print(f"Errore: Elemento non trovato - {str(e)}")
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error_type": "NoSuchElementException",
            "error": str(e),
            "current_url": driver.current_url
        }
        os.makedirs("data", exist_ok=True)
        with open("data/sentenza_oggi.json", "w", encoding="utf-8") as f:
            json.dump(error_data, f, ensure_ascii=False, indent=2)
        return False
        
    except Exception as e:
        print(f"Errore: {str(e)}")
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error_type": type(e).__name__,
            "error": str(e),
            "current_url": driver.current_url if driver else "N/A"
        }
        os.makedirs("data", exist_ok=True)
        with open("data/sentenza_oggi.json", "w", encoding="utf-8") as f:
            json.dump(error_data, f, ensure_ascii=False, indent=2)
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    success = scrape_jurisprudence()
    exit(0 if success else 1)
