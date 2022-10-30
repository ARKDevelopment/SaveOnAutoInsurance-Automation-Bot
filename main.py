import asyncio, random, datetime, requests, json
from numpy import append
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError 
from components import proxyfy, Model


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

  random_device = random.choice(device_list)
  # print(random_device)
  yield random_device
  # random_device = device_list[9]
  
  device = playwright.devices[random_device]
  # device.pop("viewport")
  # print(device)
  # system = 
  # browser = await playwright.chromium.launch(headless=False)
  browser = await playwright[playwright_device_list[1][random_device]["defaultBrowserType"]].launch(headless=False)
  
  yield await browser.new_context(**device, 
    proxy={**proxy} if proxy else None,
    # viewport={"width": 800, "height": 900}
  )
  
  

async def random_selector(page, selector:str):
  item = await page.query_selector_all(f'{selector} > option')
  item = item[1:]
  item = random.choice(item)
  item = await item.get_attribute('value')
  await page.select_option(selector, item)
  return item


async def scroller(page, wait):
  while wait > 0:
      print('AU')
      about_us = await page.query_selector('#kool')
      await about_us.scroll_into_view_if_needed()
      rem = random.randint(2000, 5000)
      await page.wait_for_timeout(rem)
      wait -= rem
      print("foot")
      foot = await page.query_selector('footer')
      await foot.scroll_into_view_if_needed()
      rem = random.randint(2000, 5000)
      await page.wait_for_timeout(rem)
      wait -= rem

async def optional_option(page, selector:str, value:str):
  if value:
    await page.select_option(selector, value)
    return value
  return ""
  


async def main(client: Model):
  async with async_playwright() as p:
    device_setting = emulated_browser(
      p, 
      proxy= None#proxyfy(client.zipp, client.city)
    )

    random_device = await device_setting.__anext__()
    print(random_device)
    
    browser = await device_setting.__anext__()

    page = await browser.new_page()
    await page.goto("http://auto.saveyourinsurance.com")
    # await page.goto("http://ifconfig.me/")

    # await page.wait_for_selector('#year')
    print("Page 1")

    wait = random.randint(2000, 10000)

    percent = int(open("percantage.txt", "r").read())
    false_array = [False] * (100-percent)
    true_array = [True] * percent
    tm = random.choice(false_array + true_array)
    if tm:
      page2 = await browser.new_page()
      await page2.goto('http://auto.saveyourinsurance.com/terms.html')
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

    year = client.year or str(random.randint(2012, int(datetime.datetime.today().year)))
    yr = await page.query_selector('#year')
    await yr.scroll_into_view_if_needed()
    await page.select_option('#year', year)
    await page.evaluate('loadVehiclMakes()')
    await page.wait_for_timeout(random.randint(2000, 4000))

    make = await optional_option(page, '#make', client.make)
    if not make:
        make = await random_selector(page, '#make')
    await page.evaluate('loadModels()')
    await page.wait_for_timeout(random.randint(2000, 4000))

    model = await optional_option(page, '#model', client.model)
    if not model:
      model = await random_selector(page, '#model')
    await page.wait_for_timeout(random.randint(2000, 4000))

    insuredform = await optional_option(page, '#insuredform', client.insuredform)
    if not insuredform:
      insuredform = await random_selector(page, '#insuredform')

    await page.check('#leadid_tcpa_disclosure')
    submit_button = await page.click('#submit')

    #PAGE 2
    print("PAGE 2")
    await page.wait_for_timeout(random.randint(4000, 6000))

    await page.type('#firstname', client.first_name, delay=random.randint(20, 120))
    await page.wait_for_timeout(random.randint(2000, 4000))

    await page.type('#lastname', client.last_name, delay=random.randint(20, 120))
    await page.wait_for_timeout(random.randint(2000, 4000))
    
    month = random.randint(1,12)
    month = month if len(str(month)) > 1 else f"0{month}"

    day = random.randint(1,28)
    day = day if len(str(day)) > 1 else f"0{day}"

    year = int(datetime.datetime.today().year) - random.randint(23, 61)
    dob = client.dob or "/".join(map(str, [month,day,year]))
    await page.type('#dateofbirth', dob, delay=random.randint(90, 200))
    await page.wait_for_timeout(random.randint(2000, 4000))

    try:
      gender = genderize(client.first_name)
    except NameError:
      gender = "Male"
    gender = client.gender.value or gender
    await page.select_option('#gender', gender)
    await page.wait_for_timeout(random.randint(2000, 4000))

    await page.type('#streetaddress', client.street_address, delay=random.randint(70, 200))
    await page.wait_for_timeout(random.randint(2000, 4000))

    await page.type('#zip', client.zipp, delay=random.randint(20, 120))
    await page.wait_for_timeout(random.randint(2000, 4000))

    await page.type('#phone', client.phone, delay=random.randint(20, 120))
    await page.wait_for_timeout(random.randint(2000, 4000))

    await page.type('#email', client.email, delay=random.randint(20, 120))

    await page.check('#liketoreceive')


    await page.wait_for_timeout(random.randint(2000, 5000))

    #Part 2
    print("Part 2")
    edu = await page.query_selector('#education')
    await edu.scroll_into_view_if_needed()

    education = await optional_option(page, '#education', client.education.value)
    if not education: 
      education = await random_selector(page, '#education')
    await page.wait_for_timeout(random.randint(2000, 4000))

    occupation = await optional_option(page, "#occupation", client.occupation)

    rating = client.rating.value or random.choice(['Good', 'Excellent'])
    await page.select_option('#creditrating', rating)
    await page.wait_for_timeout(random.randint(2000, 4000))

    married = client.rating.value or "No"
    await page.select_option('#married', married)
    await page.wait_for_timeout(random.randint(2000, 4000))

    licensed = await optional_option(page, "#licence", client.licensed.value)
    if not licensed:
      await page.wait_for_timeout(random.randint(1000, 2000))


    filling = await optional_option(page, "#filling", client.filling.value)
    if not filling:
      await page.wait_for_timeout(random.randint(1000, 2000))
    
    tickets = await optional_option(page, "#tickets", client.tickets.value)
    if not tickets:
      await page.wait_for_timeout(random.randint(1000, 2000))

    expiration = await optional_option(page, "#policy", client.expiration)
    if not expiration:
      await page.wait_for_timeout(random.randint(1000, 2000))

    covered = await optional_option(page, "#covered", client.covered.value)
    if not covered:
      await page.wait_for_timeout(random.randint(1000, 2000))

    homeowner = await optional_option(page, "#ownhome", client.homeowner.value)
    if not homeowner:
      await page.wait_for_timeout(random.randint(1000, 2000))

    submit_button = await page.query_selector('#submit >> nth=1')
    await submit_button.scroll_into_view_if_needed()
    await page.wait_for_timeout(random.randint(2000, 5000))
    data = []
    page.on('request', lambda req: data.append([req.post_data, req.post_data_json]) if req.url.endswith('submitDetails.php') else None)
    try:
      await submit_button.click(timeout=2000)
    except:
      while data == []:
        await page.wait_for_timeout(100)

    #PAGE 3
      await page.goto(f"http://auto.saveyourinsurance.com/submitDetails.php?{data[0][0]}", referer='http://auto.saveyourinsurance.com')
    await page.wait_for_timeout(random.randint(10000, 15000))

    print("Done")

    return {
    "year": year,
    "make": make,
    "model": model,
    "insuredform": insuredform,
    "first_name": client.first_name,
    "last_name": client.last_name,
    "dob": dob,
    "gender":  gender,
    "street_address": client.street_address,
    "city": client.city,
    "zipp": client.zipp,
    "phone": client.phone,
    "email":  client.email,
    "education": education,
    "occupation": occupation,
    "rating": rating,
    "married": married,
    "licensed": licensed,
    "filling": filling,
    "tickets": tickets,
    "expiration": expiration,
    "covered": covered,
    "homeowner": homeowner,
    "device": random_device, 
    "ip": data[0][1]["ipuser"]
    }


if __name__ == "__main__":
  # pass
  # asyncio.run(optional_options(ziptostate, 12345, "j"))
  # print()
  # print(playwright_devices()[1]["Blackberry PlayBook"])
  test_data = {"first_name":"testGreen", "last_name":"testG", "street_address":"test", "city":"test", "zipp":"85306", "phone":"8545214523", "email":"ds45s@gmail.com"}
  def test(data: Model):
    print(data)
  test(Model(**test_data))
  asyncio.run(main(Model(**test_data)))
  # print(playwright_devices())
  # print(genderize('John'))
