import asyncio, random, datetime, requests, json
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
  device_list = [x for x in playwright_device_list[0] if x]

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
    try:
      await page.select_option(selector, value)
    except PlaywrightTimeoutError:
      return ""
    return value
  return ""
  


async def main(client: Model):
  # print(client)
  async with async_playwright() as p:
    proxy = proxyfy(client.zipp, client.city)
    print(proxy)
    device_setting = emulated_browser(
      p, 
      proxy=proxy
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
    await page.wait_for_timeout(random.randint(3000, 4000))

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
    dob = client.dob.replace("-", "/") or "/".join(map(str, [month,day,year]))
    await page.type('#dateofbirth', dob, delay=random.randint(90, 200))
    await page.wait_for_timeout(random.randint(2000, 4000))

    try:
      gender = genderize(client.first_name)
    except NameError:
      gender = "Male"
    gender = client.gender or gender
    await page.select_option('#gender', gender.capitalize())
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

    education = await optional_option(page, '#education', client.education)
    if not education: 
      await page.wait_for_timeout(random.randint(2000, 4000))
      # education = await random_selector(page, '#education')

    occupation = await optional_option(page, "#occupation", client.occupation)

    rating = await optional_option(page, '#creditrating', client.rating)
    if not rating: 
      rating = random.choice(['Good', 'Excellent'])
      await page.select_option('#creditrating', rating)
    await page.wait_for_timeout(random.randint(2000, 4000))

    married = await optional_option(page, '#maritalstatus', client.married)
    if not married:
      married = "Single"
    await page.select_option('#maritalstatus', married)
    await page.wait_for_timeout(random.randint(2000, 4000))

    licensed = await optional_option(page, "#licence", client.licensed)
    if licensed:
      await page.wait_for_timeout(random.randint(1000, 2000))


    filling = await optional_option(page, "#filling", client.filling)
    if filling:
      await page.wait_for_timeout(random.randint(1000, 2000))
    
    tickets = await optional_option(page, "#tickets", client.tickets)
    if tickets:
      await page.wait_for_timeout(random.randint(1000, 2000))

    # covered = await optional_option(page, "#covered", client.covered)
    # if covered:
    #   await page.wait_for_timeout(random.randint(1000, 2000))

    # expiration = await optional_option(page, "#policy", client.expiration)
    # if expiration:
    #   await page.wait_for_timeout(random.randint(1000, 2000))

    if client.expiration:
      await page.type('#policy', client.expiration, delay=random.randint(90, 200))
      await page.wait_for_timeout(random.randint(2000, 4000))

    if client.insuredsince:
      await page.type('#insuredsince', client.insuredsince, delay=random.randint(90, 200))
      await page.wait_for_timeout(random.randint(2000, 4000))

    homeowner = await optional_option(page, "#ownhome", client.homeowner)
    if homeowner:
      await page.wait_for_timeout(random.randint(1000, 2000))

    submit_button = await page.query_selector('#submit >> nth=1')
    await submit_button.scroll_into_view_if_needed()
    await page.wait_for_timeout(random.randint(2000, 5000))
    data = []
    page.on('request', lambda req: data.append([req.post_data, req.post_data_json]) if req.url.endswith('submitDetails.php') else None)
    try:
      await submit_button.click(timeout=2000)
    except:
      pass
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
    "expiration": client.expiration,
    "insuredsince": client.insuredsince,
    "homeowner": homeowner,
    "device": random_device, 
    "ip": data[0][1]["ipuser"]
    }


if __name__ == "__main__":
  # pass
  # asyncio.run(optional_options(ziptostate, 12345, "j"))
  # print()
  # print(playwright_devices()[1]["Blackberry PlayBook"])
  test_data = {
    "first_name": "ms",
  	"last_name":"crosser",
    "dob": "13-10-1979",
    "gender":	"Female",
    "street_adress": "nill",
    "zip": "7933",
    "phone": "7653628415",
    "email": "mscrosser8415@gmail.com",
    "education": "Associate Degree",
    "occupation":"	Legal",	
    "rating": "Good",	
    "married": "Married",
    "license": "Yes",
    "filling": "Yes",
    "tickets": "No",
    "expiration": "13-06-2023",	
    "insuredsince": "22-08-2005",	
    "homeowner": "No",	
    "year": "1990",	
    "make": "NISSAN",	
    "model": "MICRA",	
    "insuredform": "Other"
  }

  # test_data = {"first_name":"testGreen", "last_name":"testG", "street_address":"test", "city":"test", "zipp":"85306", "phone":"8545214523", "email":"ds45s@gmail.com"}
  def test(data: Model):
    print(data)
  test(Model(**test_data))
  asyncio.run(main(Model(**test_data)))
  # print(playwright_devices())
  # print(genderize('John'))
