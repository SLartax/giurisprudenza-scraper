import os
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def make_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=opts)
    return driver

def scrape_jurisprudence():
    driver = make_driver()
    wait = WebDriverWait(driver, 30)
    
    try:
        print("Apertura banca dati giurisprudenza...")
        driver.get("https://bancadatigiurisprudenza.giustiziatributaria.gov.it/ricerca")
        
        print("Selezione anno...")
        anno_select = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//label[contains(text(),'Anno')]/parent::div//select")
        ))
        Select(anno_select).select_by_value("2025")
        
        print("Selezione esito favorevole...")
        esito_select = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//label[contains(text(),'Esito giudizio')]/parent::div//select")
        ))
        Select(esito_select).select_by_visible_text("Favorevole al contribuente")
        
        print("Avvio ricerca...")
        ricerca_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(),'Ricerca')]")
        ))
        ricerca_btn.click()
        
        print("Attesa risultati...")
        wait.until(EC.presence_of_element_located((By.XPATH, "//table")))
        
        print("Apertura prima sentenza...")
        first_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "(//a[contains(@href,'dettaglio')])[1]")
        ))
        first_link.click()
        
        print("Estrazione testo...")
        text_block = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class,'sentenza') or contains(@class,'container')]")
        ))
        
        testo = text_block.text
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
        
    except Exception as e:
        print(f"Errore: {e}")
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": str(e)
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
