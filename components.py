import re
import requests


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