import streamlit as st
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import hashlib

def fetch_url(url):
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # Run in headless mode
    options.add_argument("--disable-logging")
    # options.add_argument("--log-level=1")  # Disable unnecessary logging
    options.add_argument("--no-sandbox")  # Bypass the sandbox for Docker environments
    options.add_argument("--disable-dev-shm-usage")  # Prevent shared memory issues
    options.add_argument("--disable-gpu")  # Disable GPU acceleration
    options.add_argument("--disable-extensions")
    options.add_argument("--enable-unsafe-swiftshader")  # Disable browser extensions
    options.add_argument("--force-device-scale-factor=1")  # Improve rendering accuracy
    options.add_argument("--remote-debugging-port=9222")  # Enable debugging in headless mode

    # Initialize the WebDriver with options
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
 
    try:
        driver.get(url)
        driver.set_page_load_timeout(120) 
        time.sleep(3)  # Wait for additional content if needed
    except Exception as e:
        print(f"Error loading {url}: {e}")
        driver.quit()
        return None
    html_content = driver.page_source
    driver.quit()
    print("webpage loaded successfully ")
    return BeautifulSoup(html_content, 'html.parser')

def extract_components(soup):
    components = []
    for item in soup.find_all(True):
        component = {
            'item': item.name,
            'role': item.get('role'),
            'id': item.get('id'),
            'class': item.get('class'),
            'text': item.get_text(strip=True),
            'attrs': item.attrs
        }
        components.append(component)
    return components

def hash_component(component):
    component_str = f"{component['item']}-{component.get('id')}-{component.get('class')}-{component['text']}"
    return hashlib.md5(component_str.encode()).hexdigest()

def components_to_dict(components):
    component_dict = {}
    for component in components:
        component_key = hash_component(component)
        component_dict[component_key] = component
    return component_dict

def detect_changes(old_components, new_components):
    changes = {"ADDED": [], "REMOVED": [], "MODIFIED": []}
    old_components_dict = components_to_dict(old_components)
    new_components_dict = components_to_dict(new_components)
    
    for old_hash, old_component in old_components_dict.items():
        if old_hash not in new_components_dict:
            changes["REMOVED"].append(old_component)
        elif old_component != new_components_dict[old_hash]:
            modified_entry = {
                "original": old_component,
                "modified": new_components_dict[old_hash]
            }
            changes["MODIFIED"].append(modified_entry)

    for new_hash, new_component in new_components_dict.items():
        if new_hash not in old_components_dict:
            changes["ADDED"].append(new_component)

    return changes

def process_webpages(url1, url2):
    soup_1 = fetch_url(url1)
    soup_2 = fetch_url(url2)

    with open('old_file.html', "w", encoding="utf-8") as file:
        file.write(str(soup_1))
    with open('new_file.html', "w", encoding="utf-8") as file:
        file.write(str(soup_2))


    old_webpage_components = extract_components(soup_1)
    new_webpage_components = extract_components(soup_2)

    changes = detect_changes(old_webpage_components, new_webpage_components)

    output_data = {
        "Added components": len(changes['ADDED']),
        "Modified components": len(changes['MODIFIED']),
        "Removed components": len(changes['REMOVED']),
        "changes": changes,
    }

    output_file_path = "output_details.json"
    
    with open(output_file_path, 'w') as json_file:
        json.dump(output_data, json_file, indent=4)

    return output_file_path

st.title("Webpage Comparison Tool")

url1 = st.text_input("Enter URL 1")
url2 = st.text_input("Enter URL 2")

if st.button("Compare"):
    if url1 and url2:
        with st.spinner("Processing... Please wait."):
            try:
                output_file = process_webpages(url1, url2)
                with open(output_file, "r") as file:
                    st.success("Processing completed successfully!")
                    st.download_button("Download Results", file, file_name="output_details.json")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter both URL 1 and URL 2 before comparing.")