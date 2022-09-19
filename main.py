import asyncio, random, datetime, requests, json
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError 
from components import proxy_test


def genderize(name):
  req = requests.get(f"https://api.genderize.io/?name={name}").text
  return eval(req)["gender"].title()

def ziptostate(zip):
  req = requests.get(f"https://api.zippopotam.us/us/{zip}").text
  return eval(req)["places"][0]["state"]


def playwright_devices():
  req = requests.get("https://raw.githubusercontent.com/microsoft/playwright/main/packages/playwright-core/src/server/deviceDescriptorsSource.json").text
  return open("devices.txt").read().split("\n"), json.loads(req)

async def emulated_browser(playwright, proxy=None):
  playwright_device_list = playwright_devices()
  device_list = playwright_device_list[0]

  global random_device
  random_device = random.choice(device_list)
  # random_device = device_list[9]
  print(random_device)
  
  device = playwright.devices["Desktop Chrome"]
  device.pop("viewport")
  # print(device)
  browser = await playwright.chromium.launch(headless=False)
  # browser = await playwright[playwright_device_list[1][random_device]["defaultBrowserType"]].launch(headless=False)
  
  return await browser.new_context(**device, 
    proxy={**proxy} if proxy else None,
    # viewport={"width": 800, "height": 900}
  )
  

async def random_selector(page, selector):
  item = await page.query_selector_all(f'{selector} > option')
  item = item[1:]
  item = random.choice(item)
  item = await item.get_attribute('value')
  await page.select_option(selector, item)
  return item


async def scroller(page, wait):
  while wait > 0:
      # print(wait)
      about_us = await page.query_selector('[data-id="475a35b7"]')
      await about_us.scroll_into_view_if_needed()
      rem = random.randint(2000, 5000)
      await page.wait_for_timeout(rem)
      wait -= rem
      foot = await page.query_selector('footer')
      await foot.scroll_into_view_if_needed()
      rem = random.randint(2000, 5000)
      await page.wait_for_timeout(rem)
      wait -= rem


async def main(first_name, last_name, street_address, city, zipp, phone, email):
  async with async_playwright() as p:
    browser = await emulated_browser(p, 
      # proxy={
      #   'server': 'p.webshare.io:80',
      #   'username': 'ytdxlpex-rotate',
      #   'password': 'p5q0cxr3pvt4',
      # }
      proxy={
        'server': 'proxy.froxy.com:9000',
        'username': 'XLdek13TDI94zkFC',
        'password': proxy_test(city, zipp),
      }
    )
    # return [x for x in range(9)]

    page = await browser.new_page()
    await page.goto("http://auto.saveyourinsurance.com/")
    # await page.goto("http://ifconfig.me/")

    await page.wait_for_selector('#year')

    wait = random.randint(2000, 10000)#, 120000)

    percent = int(open("percantage.txt", "r").read())
    false_array = [False] * (100-percent)
    true_array = [True] * percent
    tm = random.choice(false_array + true_array)
    if tm:
      page2 = await browser.new_page()
      await page2.goto('http://auto.saveyourinsurance.com//terms.html', timeout=60000)
      ps = await page2.query_selector_all('p')
      for p in ps:
        if wait < 1:
          break
        await p.scroll_into_view_if_needed()
        rem = random.randint(2000, 3000)
        await page.wait_for_timeout(rem)
        wait -= rem
      await page2.close()

    await scroller(page, wait)

    year = random.randint(2012, int(datetime.datetime.today().year))
    yr = await page.query_selector('#year')
    await yr.scroll_into_view_if_needed()
    await page.select_option('#year', str(year))
    await page.evaluate('loadVehiclMakes()')
    await page.wait_for_timeout(random.randint(1000, 2000))

    
    make = await random_selector(page, '#make')
    await page.evaluate('loadModels()')
    await page.wait_for_timeout(random.randint(1000, 2000))

    model = await random_selector(page, '#model')
    await page.wait_for_timeout(random.randint(1000, 2000))

    insuredform = await random_selector(page, '#insuredform')

    await page.check('#leadid_tcpa_disclosure')
    await page.click('#submit')

    #PAGE 2
    print("PAGE 2")
    await page.wait_for_timeout(random.randint(1000, 2000))

    await page.type('#firstname', first_name, delay=random.randint(20, 120))
    await page.wait_for_timeout(random.randint(1000, 2000))

    await page.type('#lastname', last_name, delay=random.randint(20, 120))
    await page.wait_for_timeout(random.randint(1000, 2000))

    dob = "/".join(map(str, [random.randint(1,12),random.randint(1, 28),int(datetime.datetime.today().year) - random.randint(23, 61)]))
    await page.type('#dateofbirth', dob, delay=random.randint(90, 200))
    await page.wait_for_timeout(random.randint(1000, 2000))
    # await page.click('.ui-state-active')
    # await page.wait_for_timeout(random.randint(1000, 2000))

    gender = genderize(first_name)
    await page.select_option('#gender', gender)
    await page.wait_for_timeout(random.randint(1000, 2000))

    await page.type('#streetaddress', street_address, delay=random.randint(70, 200))
    await page.wait_for_timeout(random.randint(1000, 2000))

    await page.type('#zip', zipp, delay=random.randint(20, 120))
    await page.wait_for_timeout(random.randint(1000, 2000))

    await page.type('#phone', phone, delay=random.randint(20, 120))
    await page.wait_for_timeout(random.randint(1000, 2000))

    await page.type('#email', email, delay=random.randint(20, 120))

    await page.check('#liketoreceive')


    h3 = await page.query_selector('h3')
    await h3.scroll_into_view_if_needed()
    await page.wait_for_timeout(random.randint(2000, 5000))

    h3 = await page.query_selector('h3 >> nth=1')
    await h3.scroll_into_view_if_needed()
    await page.wait_for_timeout(random.randint(2000, 5000))

    

    #Part 2
    print("Part 2")
    education = await random_selector(page, '#education')
    await page.wait_for_timeout(random.randint(1000, 2000))

    await page.wait_for_timeout(random.randint(1000, 2000))

    rating = random.choice(['Good', 'Excellent'])
    await page.select_option('#creditrating', rating)
    await page.wait_for_timeout(random.randint(1000, 2000))

    await page.select_option('#married', "No")
    await page.wait_for_timeout(random.randint(1000, 2000))

    await page.select_option('#tickets', "No")
    await page.wait_for_timeout(random.randint(1000, 2000))


    submit_button = await page.query_selector('#submit >> nth=1')
    await submit_button.scroll_into_view_if_needed()
    await page.wait_for_timeout(random.randint(2000, 5000))
    await submit_button.click()

    #PAGE 3
    await page.wait_for_timeout(random.randint(10000, 30000))
    print("Done")

    return year, make, model, insuredform, dob, gender, education, rating, random_device


if __name__ == "__main__":
  # proxy_test()
  asyncio.run(main(first_name="keyla", last_name="Doe", street_address="123 Main St", city="new york", zipp="54545", phone="1234567890", email="flkflkf@lkdf.dmm"))
  # print(playwright_devices())
  # print(genderize('John'))