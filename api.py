import csv, sqlite3, uuid, pandas
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse
from pydantic import BaseModel
from components import proxy_test, email_verified, log_html, percent_html


app = FastAPI()


conn = sqlite3.connect('autoinsurance.db')
cur = conn.cursor()

for table in ["queue","errors"]:
    cur.execute(f"""CREATE TABLE IF NOT EXISTS {table} (
    id TEXT,
    first_name TEXT,
    last_name TEXT,
    street_address TEXT,
    city TEXT,
    zip TEXT,
    phone TEXT,
    email TEXT
        ); """
    )

conn.commit()
conn.close()


class AutoInsurance(BaseModel):
    first_name: str
    last_name: str
    street_address: str
    city: str
    zipp: str
    phone: str
    email: str


def sql_to_csv(name):
    con = sqlite3.connect('autoinsurance.db')
    cur = con.cursor()
    cmd = cur.execute("SELECT * FROM log")[::-1]

    with open(name, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Id",
                "First Name",
                "Last Name",
                "Street Address",
                "zip",
                "Phone",
                "email",
                "Year",
                "Make",
                "Model",
                "Insured From",
                "DOB",
                "Gender",
                "Device",
                "Education",
                "Rating",
                "Status"
            ]
        )

        writer.writerows(cmd)

    con.close()

class AddToSQL:
    def __init__(self, first_name, last_name, street_address, city, zipp, phone, email):
        self.first_name = first_name
        self.last_name = last_name
        self.street_address = street_address
        self.city = city
        self.zipp = zipp
        self.phone = phone
        self.email = email

    def exec(self, table, idd):
        con = sqlite3.connect('autoinsurance.db')
        self.cur = con.cursor()
        self.cur.execute(f"""INSERT INTO {table} (
            id, 
            first_name, 
            last_name, 
            street_address, 
            city, 
            zip, 
            phone, 
            email
            ) 
            VALUES ({"?, "*7}?)""", 
            (
                idd,
                self.first_name,
                self.last_name,
                self.street_address,
                self.city,
                self.zipp,
                self.phone,
                self.email
            )
        )
        con.commit()
        con.close()
    

@app.get("/")
async def get():
    return HTMLResponse(percent_html)


@app.websocket("/percent")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_text()
            int(data)
            open("percantage.txt", "w").write(data)
            await websocket.send_text(f"Click T&S percentage updated to: {data}")
        except ValueError:
            await websocket.send_text("Invalid Input! Make sure not to include any letters or symbols.")


@app.get("/log")
async def get():
    return HTMLResponse(log_html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        sql_to_csv('ws.csv')
        file = pandas.read_csv('ws.csv')
        await websocket.send_text(file.to_html())
        
        # con = sqlite3.connect('autoinsurance.db')
        # cur = con.cursor()
        # cmd = cur.execute("SELECT * FROM log")
        # data = cmd.fetchall()
        # new_data = "<br/>".join([", ".join(x) for x in data])
        # con.close()
        # await websocket.send_text(new_data)


@app.get('/{table}')
def list_view(table):
    try:
        con = sqlite3.connect('autoinsurance.db')
        cur = con.cursor()
        cmd = cur.execute(f"SELECT * FROM {table}")
        data = cmd.fetchall()
        # data_str = "<br/>".join(list(data))
        con.close()
        return data
    except:
        return HTMLResponse("<h1>Invalid Address</h1>")


@app.post('/add-to-queue')
async def automate(auto_insurance: AutoInsurance):
    idd = str(uuid.uuid4())
    add_to_sql = AddToSQL(auto_insurance.first_name, auto_insurance.last_name, auto_insurance.street_address, auto_insurance.city, auto_insurance.zipp, auto_insurance.phone, auto_insurance.email)
    if not email_verified(auto_insurance.email): 
        add_to_sql.exec("errors", "Invalid Email")
        return "ERROR 400: Invalid Email!"
        # raise HTTPException(status_code=400, detail="Invalid email address")

    if len(auto_insurance.zipp.strip()) < 4 and len(auto_insurance.zipp.strip()) > 5:
        add_to_sql.exec("errors", "Invalid Zip")
        return {"ERROR 400": "Invalid Zip Code!"}
    elif len(auto_insurance.zipp.strip()) == 4:
        auto_insurance.zipp = "0" + auto_insurance.zipp.strip()
    # raise HTTPException(status_code=400, detail="Invalid Zip Code")    

    try:
        proxy_test(auto_insurance.city, auto_insurance.zipp)
    except Exception as e:
        add_to_sql.exec("errors", e)
        return f"ERROR 400: {e}"
        # raise HTTPException(status_code=400, detail="No proxies available for this zip code")

    add_to_sql.exec("queue", idd)
    return idd


@app.get('/download')
def download_as_csv():
    sql_to_csv("logs.csv")
    return FileResponse('logs.csv', media_type='text/csv', filename='logs.csv')

@app.get('/delete/{id}')
def delete(id):
    con = sqlite3.connect('autoinsurance.db')
    cur = con.cursor()
    cur.execute(f"DELETE FROM queue WHERE id='{id}'")
    cur.execute(f"DELETE FROM log WHERE id='{id}'")
    con.commit()
    con.close()
    return "Deleted!"
