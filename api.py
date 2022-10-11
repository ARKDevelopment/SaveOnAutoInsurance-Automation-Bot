import csv, sqlite3, uuid, pandas
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse
from pydantic import BaseModel
from components import proxyfy, email_verified, log_html, percent_html

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
    email TEXT,
    timestamp TIMESTAMP
        ); """
    )

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
ip TEXT,
status TEXT,
timestamp TIMESTAMP
); """
)

conn.commit()
conn.close()


class AutoInsurance(BaseModel):
    first_name: str = ""
    last_name: str = ""
    street_address: str = ""
    city: str = ""
    zipp: str = ""
    phone: str = ""
    email: str = ""


def sql_to_csv(name):
    con = sqlite3.connect('autoinsurance.db')
    cur = con.cursor()
    cmd = cur.execute("SELECT * FROM log")

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
                "Education",
                "Rating",
                "Device",
                "Ip",
                "Status",
                "Time Stamp"
            ]
        )

        log_rev = [*cmd][::-1]
        writer.writerows(log_rev)

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

    def add_to_log(self, idd, status, holder):
        con = sqlite3.connect('autoinsurance.db')
        self.cur = con.cursor()
        self.cur.execute(f"""INSERT INTO log (
            id,
            first_name,
            last_name,
            street_address,
            zip,
            phone,
            email,
            year,
            make,
            model,
            insuredform,
            dob,
            gender,
            education,
            rating,
            device,
            ip,
            status
            )
            values ({"?, "*17}?)""",
            (
                idd,
                self.first_name,
                self.last_name,
                self.street_address,
                self.zipp,
                self.phone,
                self.email
                *[holder] *10,
                status
            )
        )


    

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


@app.get('/log/{table}')
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

    missing_items = [k for k,v in auto_insurance.dict().items() if v == ""]
    print(auto_insurance.dict().items())
    if len(missing_items) > 0:
        add_to_sql.add_to_log("errors", "Missing " + ", ".join(missing_items), "x")
        raise HTTPException(status_code=400, detail="Missing " + ", ".join(missing_items))
    
            
    if not email_verified(auto_insurance.email): 
        add_to_sql.add_to_log("errors", "Invalid Email", "x")
        # return "ERROR 400: Invalid Email!"
        raise HTTPException(status_code=404, detail="Invalid email address")

    if len(auto_insurance.zipp.strip()) not in [4, 5]:
        add_to_sql.add_to_log("errors", "Invalid Zip", "x")
        raise HTTPException(status_code=404, detail="Invalid Zip Code")
        # return {"ERROR 400": "Invalid Zip Code!"}
    elif len(auto_insurance.zipp.strip()) == 4:
        auto_insurance.zipp = "0" + auto_insurance.zipp.strip()

    try:
        proxyfy(auto_insurance.zipp, auto_insurance.city)
        add_to_sql.exec("queue", idd)
        add_to_sql.add_to_log(idd, "queue", "?")
    except Exception as e:
        add_to_sql.add_to_log("errors", str(e), "x")
        raise HTTPException(status_code=404, detail=e)
        # raise HTTPException(status_code=400, detail="No proxies available for this zip code")


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