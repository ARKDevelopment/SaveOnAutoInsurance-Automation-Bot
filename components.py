from pydantic import BaseModel
from enum import Enum
import random
import re
import requests


class Gender(Enum):
    blank = ""
    male = "Male"
    female = "Female"

class YesNo(Enum):
    blank = ""
    yes = "Yes"
    no = "No"

class Rating(Enum):
    blank = ""
    poor = "Poor"
    fair = "Fair"
    good = "Good"
    average = "Average"
    unsure = "Unsure"
    excellent = "Excellent"
    superior = "Superior"

class Covered(Enum):
    blank = ""
    less_six_months = "Less Than 6 months"
    six_months = "6 Months"
    one_year = "1 Year"
    two_year = "2 Years"
    three_year = "3 Years"
    three_five_year = "3-5 Years"
    more_fix_year = "More Than 5 Years"

class Model(BaseModel):
    year: str = ""
    make: str = ""
    model: str = ""
    insuredform: str = ""
    first_name: str = ""
    last_name: str = ""
    dob: str = ""
    gender: str = ""
    street_address: str = ""
    city: str = ""
    zipp: str = ""
    phone: str = ""
    email: str = "" 
    education: str = ""
    occupation: str = ""
    rating: str = ""
    married: str = ""
    licensed: str = ""
    filling: str = ""
    tickets: str = ""
    expiration: str = ""
    insuredsince: str = ""
    covered: str = ""
    homeowner: str = ""


percent_html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Percentage</title>
    </head>
    <body>
        <h1>Percentage Changer</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://45.79.124.51:8000//percent");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


def ziptostate(zip):
    req = requests.get(f"https://api.zippopotam.us/us/{zip}").text
    try:
        return eval(req)["places"][0]
    except KeyError:
        raise Exception("Invalid zip code")


def email_verified(email):
    if re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        return True
    return 


def froxy_proxy(state, city):
    #proxy test for city and zip to get password
    state = state.lower().replace(" ", "+")
    port = str(random.randint(9000, 9015))

    try:
        password = f'wifi;us;;{state};{city}'
        proxies = {"https" : f'http://XLdek13TDI94zkFC:{password}@proxy.froxy.com:{port}'}
        r = requests.get("https://ifconfig.me", proxies=proxies)
    except requests.exceptions.ProxyError:
        try:
            password = f'wifi;us;;{state};'
            proxies = {"https" : f'http://XLdek13TDI94zkFC:{password}@proxy.froxy.com:{port}'}
            r = requests.get("https://ifconfig.me", proxies=proxies)
        except requests.exceptions.ProxyError:
            return
    return {
        "server": f"proxy.froxy.com:{port}",
        "username": "XLdek13TDI94zkFC",
        "password": password
  } 


def smart_proxy(state):
    #random proxy test
    url = "https://api.smartproxy.com/v1/endpoints/sticky"

    headers = {"accept": "application/json"}

    response = requests.get(url, headers=headers)

    for i in response.json():
        if i["location"] == state.title():
            return {"server":i["hostname"] + ":" + str(random.randint(*map(int, i["port_range"].replace(" ", "").split("-")))),
                    "username": "sp55359177",
                    "password": "sp55359177"}
    return

    # print(response.json())


def proxyfy(zipp, city):
    state = ziptostate(zipp)["state"]
    proxy = [x for x in [froxy_proxy(state, city), smart_proxy(state)] if x]
    try:
        proxy = random.choice(proxy)
    except IndexError:
        raise Exception("No proxy available for this location")
    
    return proxy


if  "__main__" == __name__:
    print(proxyfy('100005', 'new york'))
#   print(email_verified("kfjdsljf@kdjf.com"))
#   print(proxy_test("New rochelle", "10801"))
    # random.choice([])
