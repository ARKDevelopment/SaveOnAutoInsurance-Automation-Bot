import time
from main import main
import asyncio
import sqlite3
from components import Model 

conn = sqlite3.connect('autoinsurance.db')
cur = conn.cursor()


cur.execute("""CREATE TABLE IF NOT EXISTS log (
  id TEXT,
  first_name TEXT,
  last_name TEXT,
  dob TEXT,
  gender TEXT,
  street_address TEXT,
  zip TEXT,
  phone TEXT,
  email TEXT,
  education TEXT,
  occupation TEXT,
  rating TEXT,
  marriege TEXT,
  licensed TEXT,
  filling TEXT,
  tickets TEXT,
  expiration TEXT,
  covered TEXT,
  homeowner TEXT,
  year TEXT,
  make TEXT,
  model TEXT,
  insuredform TEXT,
  device TEXT,
  ip TEXT,
  status TEXT,
  date DATE DEFAULT CURRENT_DATE,
  time TIME DEFAULT CURRENT_TIME
); """
)

async def sql_delete(item):
  items = array_to_dict(item)
  print(items)
  idd = items["id"]
  print(idd)
  print(items)
  try:
    # Check and delete old log
    # cur.execute("DELETE FROM log WHERE id = ?", (idd,))
    # conn.commit()

    # Inserting into log and making random data unknown
    cur.execute("UPDATE log SET status = ? WHERE id = ?", ('running', idd,))
    # cur.execute("INSERT INTO log (id, first_name, last_name, street_address, zip, phone, email, year, make, model, insuredform, dob, gender, device, ip, education, rating, status) VAlUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
    #                               (item[0],item[1],item[2],item[3],item[5],item[6],item[7], "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", 'running'))
    conn.commit()

    values = await main(Model(**items))

    # Update Random Values into log
    cur.execute("""UPDATE log SET  
      first_name = ?,
      last_name = ?,
      dob = ?,
      gender = ?,
      street_address = ?,
      zip = ?,
      phone = ?,
      email = ?,
      education = ?,
      occupation = ?,
      rating = ?,
      marriege = ?,
      licensed = ?,
      filling = ?,
      tickets = ?,
      expiration = ?,
      covered = ?,
      homeowner = ?,
      year = ?,
      make = ?,
      model = ?,
      insuredform = ?,
      device = ?,
      ip = ?,
      status = ?
      WHERE id=?""", 
    (
      values["first_name"],
      values["last_name"],
      values["dob"],
      values["gender"],
      values["street_address"],
      values["zipp"],
      values["phone"],
      values["email"],
      values["education"],
      values["occupation"],
      values["rating"],
      values["married"],
      values["licensed"],
      values["filling"],
      values["tickets"],
      values["expiration"],
      values["covered"],
      values["homeowner"],
      values["year"],
      values["make"],
      values["model"],
      values["insuredform"],
      values["device"],
      values["ip"],
      "success",
      idd,))
    conn.commit()

    # Remove from queue
    cur.execute("DELETE FROM queue WHERE id = ?", (idd,))

    # Update log
    # cur.execute("UPDATE log SET status = ? WHERE id = ?", ('success', idd,))
    conn.commit()
    return True
    
  except Exception as e:
    # Update log if error
    error_msg = str(e).replace("=", "").replace("logs", "").replace(",", ".")
    cur.execute("UPDATE log SET status = ? WHERE id = ?", (error_msg, idd))
    conn.commit()
    print(e)
    return True
  

async def send_to_process(queue_items):
  await asyncio.gather(*[sql_delete(x) for x in queue_items])

def array_to_dict(queue_item: list):
  key =  [
    "id",
    "first_name",
    "last_name",
    "dob",
    "gender",
    "street_address",
    "city",
    "zipp",
    "phone",
    "email",
    "education",
    "occupation",
    "rating",
    "married",
    "licensed",
    "filling",
    "tickets",
    "expiration",
    "covered",
    "homeowner",
    "year",
    "make",
    "model",
    "insuredform",
    "date",
    "time"]

  return dict(zip(key, queue_item))

def main_loop():
  while True:
    cmd = cur.execute("SELECT * FROM queue").fetchall()
    queue_items = [x for x in cmd]

    # Taking all from queue if less than 5 otherwise taking 5
    try:
      if len(queue_items) < 10 and len(queue_items) > 0:
        asyncio.run(
          asyncio.wait_for(
            send_to_process(queue_items), 
            timeout=360)
            )
      elif len(queue_items) >= 10:
        asyncio.run(
          asyncio.wait_for(
            send_to_process(queue_items[:10]),
             timeout=360)
             )
    except asyncio.TimeoutError:
      print("Timeout Error")
      pass
      # asyncio.run(send_to_process(queue_items[:5]))

    time.sleep(2)

if __name__ == "__main__":
  try:
    # array_to_dict(('4841f142-fb78-490b-a739-78a403ac0e72', 'w', 'w', '', '', '11', 'aa', '12345', '9191', 'aa@ss.com', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '2022-10-30', '07:39:29'))
    main_loop()
  except KeyboardInterrupt:
    exit()
