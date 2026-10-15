from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://script.google.com/a/macros/simsburyschools.net/s/AKfycbzF4gggoAuw3EN6IJU6z-K9ay6cWCdicMXVfMD2VeI-6ShPaT5laDJGmCZkTCeMombx/exec")

# 1. Locate the iframe element
iframe = driver.find_element(By.CSS_SELECTOR, "iframe#my-iframe")

# 2. Switch focus to the iframe
driver.switch_to.frame(iframe)

# 3. Interact with elements inside the iframe
heading = driver.find_element(By.TAG_NAME, "h1")
print(heading.text)

# 4. Switch back to the main page content
driver.switch_to.default_content()

driver.quit()
