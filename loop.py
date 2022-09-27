import os
import time
from uuid import uuid4
from main import main
import asyncio
import sqlite3

conn = sqlite3.connect('autoinsurance.db')
cur = conn.cursor()


cur.execute("""CREATE TABLE IF NOT EXISTS log (
id TEXT,
first_name TEXT,
last_name TEXT,
street_address TEXT,
zip TEXT,
phone TEXT,
email TEXT,
year TEXT,
make TEXT,
model TEXT,
insuredform TEXT,
dob TEXT,
gender TEXT,
education TEXT,
rating TEXT,
device TEXT,
status TEXT
); """
)


async def sql_delete(item):
  idd = item[0]
  print(idd)
  print(item)
  try:
    # Check and delete old log
    cur.execute("DELETE FROM log WHERE id = ?", (idd,))
    conn.commit()

    # Inserting into log and making random data unknown
    cur.execute("INSERT INTO log (id, first_name, last_name, street_address, zip, phone, email, year, make, model, insuredform, dob, gender, device, education, rating, status) VAlUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                                  (item[0],item[1],item[2],item[3],item[5],item[6],item[7], "?", "?", "?", "?", "?", "?", "?", "?", "?", 'running'))
    conn.commit()

    random_values = await main(*list(item[1:]))

    # Update Random Values into log
    cur.execute("UPDATE log SET year=?, make=?, model=?, insuredform=?, dob=?, gender=?, education=?, rating=?, device=?, status=? WHERE id=?", 
    (random_values[0], random_values[1], random_values[2], random_values[3], random_values[4], random_values[5], random_values[6], random_values[7], random_values[8], 'completed', idd,))
    # cur.execute("UPDATE log (id, first_name, last_name, street_address, zip, phone, email, year, make, model, insured, device, status) VAlUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (*item, *random_values, 'queued'))
    conn.commit()

    # Remove from queue
    cur.execute("DELETE FROM queue WHERE id = ?", (idd,))

    # Update log
    cur.execute("UPDATE log SET status = ? WHERE id = ?", ('success', idd,))
    conn.commit()
    return True
    
  except Exception as e:
    # Update log if error
    error_msg = str(e).replace("=", "").replace("logs", "").replace(",", ".")
    cur.execute("UPDATE log SET status = ? WHERE id = ?", (error_msg, idd))
    conn.commit()
    print(e)
    return False
  

async def send_to_process(queue_items):
  await asyncio.gather(*[sql_delete(x) for x in queue_items])

def main_loop():
  while True:
    cmd = cur.execute("SELECT * FROM queue").fetchall()
    queue_items = [x for x in cmd]

    # Taking all from queue if less than 5 otherwise taking 5
    if len(queue_items) < 5 and len(queue_items) > 0:
      asyncio.run(send_to_process(queue_items))
    elif len(queue_items) >= 5:
      asyncio.run(send_to_process(queue_items[:5]))

    time.sleep(5)

if __name__ == "__main__":
  try:
    main_loop()
  except KeyboardInterrupt:
    exit()