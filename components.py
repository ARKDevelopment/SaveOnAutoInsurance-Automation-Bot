import re
import requests


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
            var ws = new WebSocket("ws://159.89.92.12:8000/percent");
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

log_html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Logs</title>
    </head>
    <body>
        <div>
        <a href='/download' style='float:right'>Download csv</a>
        </div>
        <h3>Id, First Name, Last Name, Street Address, Zip, Phone, Email, Status</h2>
        <div id="log-body"></div>
        <script>
            var ws = new WebSocket("ws://http://159.89.92.12:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('log-body')
                var content = document.createTextNode(event.data)
                messages.innerHTML = content.textContent
            };
             setInterval(() => ws.send('DataRequest'), 100)
        </script>
    </body>
</html>
"""



def ziptostate(zip):
  req = requests.get(f"https://api.zippopotam.us/us/{zip}").text
  return eval(req)["places"][0]


def email_verified(email):
  if re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
    return True
  return False


def proxy_test(city, zipp):
  try:
      state = ziptostate(zipp)["state"].lower().replace(" ", "+")
  except KeyError:
      raise Exception("Invalid zip code")

  try:
      # city = city.lower().replace(" ", "+")
      password = f'wifi;us;;{state};{city}'
      # password = 'wifi;us;;{state};'
      # print(password)
      proxies = {"https" : f'http://XLdek13TDI94zkFC:{password}@proxy.froxy.com:9001'}
      r = requests.get("https://api.ipify.org", proxies=proxies)
      # print(r.text)
  except requests.exceptions.ProxyError:
      try:
        password = f'wifi;us;;{state};'
        proxies = {"https" : f'http://XLdek13TDI94zkFC:{password}@proxy.froxy.com:9001'}
        r = requests.get("https://tools.keycdn.com", proxies=proxies)
      except requests.exceptions.ProxyError:
        raise Exception("No proxy available for this location")
      
  return password


if  "__main__" == __name__:
  print(email_verified("kfjdsljf@kdjf.com"))
  # print(proxy_test("New Yordfdfk", "10001"))