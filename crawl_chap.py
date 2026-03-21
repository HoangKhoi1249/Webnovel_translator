import json
import os
import time
import hashlib
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def load_state(state_file):
    if not os.path.exists(state_file):
        return None

    try:
        with open(state_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            return None

        last = lines[-1]

        parts = last.split("|")
        page = int(parts[1].split("=")[1].strip())
        url = parts[2].split("=")[1].strip()

        hashes = set()

        for line in lines:
            if "HASH=" in line:
                h = line.split("HASH=")[1].strip()
                hashes.add(h)

        return {
            "CurrentPage": page,
            "LastUrl": url,
            "Hashes": hashes
        }
    except:
        return None
    
def save_state(state_file, page_index, current_url, content_hash):
    line = f"{datetime.now().isoformat()} | PAGE={page_index} | URL={current_url} | HASH={content_hash}\n"

    with open(state_file, "a", encoding="utf-8") as f:
        f.write(line)


# =========================
# CONFIG
# =========================
def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# LOGGER
# =========================
def init_logger(LogDir):
    os.makedirs(LogDir, exist_ok=True)
    log_file = os.path.join(LogDir, datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log"))
    return log_file


def write_log(log_file, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# =========================
# DRIVER
# =========================
def init_driver(headless=True):
    options = Options()

    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    return webdriver.Chrome(options=options) # type: ignore


# =========================
# SAVE HTML
# =========================
def save_html(content, name_url, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{name_url}.html")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return file_path


# =========================
# CLICK LOGIC (3 tầng)
# =========================
def click_button(driver, wait, log_file, primary, secondary, keywords, try_text=False):
    if not try_text:
        # --- 1. PRIMARY ---
        try:
            btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, primary)))
            btn.click()
            write_log(log_file, "[+] Click PRIMARY")
            return True
        except:
            write_log(log_file, "[!] Primary fail")

        # --- 2. SECONDARY ---
        try:
            btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, secondary)))
            btn.click()
            write_log(log_file, "[+] Click SECONDARY")
            return True
        except:
            write_log(log_file, "[!] Secondary fail")

    # --- 3. TEXT ---
    for keyword in keywords:
        try:
            xpath = f"""
            //button[.//text()[contains(., '{keyword}')]] |
            //a[.//text()[contains(., '{keyword}')]]
            """

            btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            driver.execute_script("arguments[0].click();", btn)

            write_log(log_file, f"[+] Click TEXT: {keyword}")
            return True
        except:
            continue

    write_log(log_file, "[X] No button found")
    return False


# =========================
# MAIN
# =========================
def main():
    config = load_config()

    start_url = config["StartUrl"]
    PrimaryButton = config["PrimaryButton"]
    SecondaryButton = config["SecondaryButton"]
    TextKeywords = config["TextKeywords"]

    MaxPages = config["MaxPages"]
    WaitTimeout = config["WaitTimeout"]

    OutputDir = config["OutputDir"]
    LogDir = config["LogDir"]

    Headless = config.get("Headless", True)
    EnableResume = config.get("EnableResume", False)
    StateFile = config.get("StateFile", "crawl.state.json")

    log_file = init_logger(LogDir)
    driver = init_driver(Headless)
    wait = WebDriverWait(driver, WaitTimeout)
    state = load_state(StateFile) if EnableResume else None

    start_page = state["CurrentPage"] if state else 0
    initial_url = start_url
    start_url = state["LastUrl"] if state and state["LastUrl"] else initial_url

    write_log(log_file, "=== START SESSION ===")
    seen_hashes = state["Hashes"] if state and "Hashes" in state else set()
    try:
        driver.get(start_url)
        

        write_log(log_file, f"[+] Start from page {start_page} : {start_url}")
        for i in range(MaxPages):
            duplicate_count = 0
            name = driver.current_url.split("/")[-1][:50]
            name = name.replace('.html', '')  # Remove .html extension if present
            
            write_log(log_file, f"[+] Processing page {i} : {driver.current_url}")

            html = driver.page_source
            content_hash = hashlib.md5(html.encode("utf-8")).hexdigest()

            if content_hash in seen_hashes:
                duplicate_count += 1
                write_log(log_file, f"[!] Duplicate content → SKIP ({duplicate_count})")

                

        
                time.sleep(2)
                
            else:
                seen_hashes.add(content_hash)
                # --- SAVE HTML ---
                html = driver.page_source
                file_path = os.path.join(OutputDir, f"{name}.html")

                if os.path.exists(file_path):
                    write_log(log_file, f"[=] Skip existing: {file_path}")
                else:
                    html = driver.page_source
                    save_html(html, name, OutputDir)
                    write_log(log_file, f"[+] Saved: {file_path}")

                if EnableResume:
                    current_url = driver.current_url
                    save_state(StateFile, i + 1, current_url, content_hash)
                    write_log(log_file, f"[+] State saved: page {i+1}")

            # --- CLICK NEXT ---
            success = click_button(
                driver,
                wait,
                log_file,
                PrimaryButton,
                SecondaryButton,
                TextKeywords,
                try_text=True
            )

            if not success:
                write_log(log_file, "[X] STOP: No more navigation")
                break

            time.sleep(2)
            

    finally:
        driver.quit()
        write_log(log_file, "=== END SESSION ===")



if __name__ == "__main__":
    main()

"""
    try:
        driver.get(start_url)
        

        write_log(log_file, f"[+] Start from page {start_page} : {start_url}")
        for i in range(MaxPages):
            duplicate_count = 0
            name = driver.current_url.split("/")[-1][:50]
            name = name.replace('.html', '')  # Remove .html extension if present
            
            write_log(log_file, f"[+] Processing page {i} : {driver.current_url}")

            html = driver.page_source
            content_hash = hashlib.md5(html.encode("utf-8")).hexdigest()

            if content_hash in seen_hashes:
                duplicate_count += 1
                write_log(log_file, f"[!] Duplicate content → SKIP ({duplicate_count})")

                

        
                time.sleep(2)
                continue

            seen_hashes.add(content_hash)

            # --- SAVE HTML ---
            html = driver.page_source
            file_path = os.path.join(OutputDir, f"{name}.html")

            if os.path.exists(file_path):
                write_log(log_file, f"[=] Skip existing: {file_path}")
            else:
                html = driver.page_source
                save_html(html, name, OutputDir)
                write_log(log_file, f"[+] Saved: {file_path}")

            if EnableResume:
                current_url = driver.current_url
                save_state(StateFile, i + 1, current_url, content_hash)
                write_log(log_file, f"[+] State saved: page {i+1}")

            # --- CLICK NEXT ---
            success = click_button(
                driver,
                wait,
                log_file,
                PrimaryButton,
                SecondaryButton,
                TextKeywords,
                try_text=True
            )

            if not success:
                write_log(log_file, "[X] STOP: No more navigation")
                break

            time.sleep(2)
            

    finally:
        driver.quit()
        write_log(log_file, "=== END SESSION ===")

"""