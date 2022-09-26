import os
from time import sleep
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
  try:
    browser = p.chromium.connect_over_cdp('http://localhost:9222')
  except:
    os.system("xvfb-run -a chromium --remote-debugging-port=9222 --no-sandbox")
    sleep(5)
    browser = p.chromium.connect_over_cdp('http://localhost:9222')
  page = browser.new_page()
  page.goto("https://wizzair.com/en-gb#/booking/select-flight/WAW/MAD/2022-10-17/null/1/0/0/null")
  page.click("button >> text=Allow all", timeout=0)
  price = page.locator('[data-test="current-price"]').first.inner_text().replace("‎", "")
  open("result.txt", "w").write(price)