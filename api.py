import csv, sqlite3, uuid, pandas, datetime
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse
import components
from components import Model as AutoInsurance


app = FastAPI()

conn = sqlite3.connect('autoinsurance.db')
cur = conn.cursor()

for table in ["queue","errors"]:
    cur.execute(f"""CREATE TABLE IF NOT EXISTS {table} (
    id TEXT,
    first_name TEXT,
    last_name TEXT,
    dob TEXT,
    gender TEXT,
    street_address TEXT,
    city TEXT,
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
    insuredsince TEXT,
    homeowner TEXT,
    year TEXT,
    make TEXT,
    model TEXT,
    insuredform TEXT,
    date DATE DEFAULT CURRENT_DATE,
    time TIME DEFAULT CURRENT_TIME
        ); """
    )

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
    insuredsince TEXT,
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

conn.commit()
conn.close()



    


class AddToSQL:
    def __init__(self, autoinsurance: AutoInsurance):
        self.details = autoinsurance
        print(self.details)

    def validate_missing(self):
        missing = []
        if self.details.first_name == "":
            missing.append("first_name")
        if self.details.last_name == "":
            missing.append("last_name")
        if self.details.street_address == "":
            missing.append("street_address")
        if self.details.city == "":
            missing.append("city")
        if self.details.zipp == "":
            missing.append("zipp")
        if self.details.phone == "":
            missing.append("phone")
        if self.details.email == "":
            missing.append("email")
        return missing


    def exec(self, table, idd):
        con = sqlite3.connect('autoinsurance.db')
        self.cur = con.cursor()
        self.cur.execute(f"""INSERT INTO {table} (
            id,
            first_name,
            last_name,
            dob,
            gender,
            street_address,
            city,
            zip,
            phone,
            email,
            education,
            occupation,
            rating,
            marriege,
            licensed,
            filling,
            tickets,
            expiration,
            insuredsince,
            homeowner,
            year,
            make,
            model,
            insuredform
            ) 
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                idd,
                self.details.first_name,
                self.details.last_name,
                self.details.dob,
                self.details.gender,
                self.details.street_address,
                self.details.city,
                self.details.zipp,
                self.details.phone,
                self.details.email,
                self.details.education,
                self.details.occupation,
                self.details.rating,
                self.details.married,
                self.details.licensed,
                self.details.filling,
                self.details.tickets,
                self.details.expiration,
                self.details.insuredsince,
                self.details.homeowner,
                self.details.year,
                self.details.make,
                self.details.model,
                self.details.insuredform
            )
        )
        con.commit()
        con.close()


    def log(self, idd, status, holder):
        con = sqlite3.connect('autoinsurance.db')
        self.cur = con.cursor()
        self.cur.execute(f"""INSERT INTO log (
            id,
            first_name,
            last_name,
            dob,
            gender,
            street_address,
            zip,
            phone,
            email,
            education,
            occupation,
            rating,
            marriege,
            licensed,
            filling,
            tickets,
            expiration,
            insuredsince,
            homeowner,
            year,
            make,
            model,
            insuredform,
            status
            )
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                idd,
                self.details.first_name,
                self.details.last_name,
                self.details.dob,
                self.details.gender,
                self.details.street_address,
                self.details.zipp,
                self.details.phone,
                self.details.email,
                self.details.education,
                self.details.occupation,
                self.details.rating,
                self.details.married,
                self.details.licensed,
                self.details.filling,
                self.details.tickets,
                self.details.expiration,
                self.details.insuredsince,
                self.details.homeowner,
                self.details.year,
                self.details.make,
                self.details.model,
                self.details.insuredform,
                status
            )
        )
        con.commit()
        con.close()


def sql_to_csv(name, funct):
    con = sqlite3.connect('autoinsurance.db')
    cur = con.cursor()
    cmd = cur.execute(funct)

    with open(name, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "id",
                "first_name",
                "last_name",
                "dob",
                "gender",
                "street_address",
                "zip",
                "phone",
                "email",
                "education",
                "ocuupation",
                "rating",
                "marriege",
                "licensed",
                "filling",
                "tickets",
                "expiration",
                "insuredsince",
                "homeowner",
                "year",
                "make",
                "model",
                "insuredform",
                "device",
                "ip",
                "status",
                "date",
                "time"
            ]
        )

        log_rev = [*cmd][::-1]
        writer.writerows(log_rev)

    con.close()


@app.get("/")
async def get():
    return HTMLResponse(components.percent_html)


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
    log_html = open("log.html").read()
    return HTMLResponse(log_html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        sql_to_csv('ws.csv', "SELECT * FROM log")
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
        # data_str = "<br>".join([str(cmd) for cmd in cmd])
        # data_str = " ".join([*cmd])
        con.close()
        return data
    except KeyboardInterrupt:
        return HTMLResponse("<h1>Invalid Address</h1>")


@app.post('/add-to-queue')
async def automate(auto_insurance: AutoInsurance):
    # print(auto_insurance)
    print(auto_insurance.education)
    idd = str(uuid.uuid4())
    add_to_sql = AddToSQL(auto_insurance)

    missing_items = add_to_sql.validate_missing()
    # print(auto_insurance.dict().items())
    if len(missing_items) > 0:
        msg = "Missing " + ", ".join(missing_items)
        add_to_sql.exec("errors", msg)
        add_to_sql.log("errors", msg, "x")
        raise HTTPException(status_code=404, detail="Missing " + ", ".join(missing_items))
    
    if not components.email_verified(auto_insurance.email): 
        add_to_sql.exec("errors", "Invalid Email")
        add_to_sql.log("errors", "Invalid Email", "x")
        # return "ERROR 400: Invalid Email!"
        raise HTTPException(status_code=404, detail="Invalid email address")

    if len(auto_insurance.zipp.strip()) not in [4, 5]:
        add_to_sql.exec("errors", "Invalid Zip")
        add_to_sql.log("errors", "Invalid Zip", "x")
        raise HTTPException(status_code=404, detail="Invalid Zip Code")
        # return {"ERROR 400": "Invalid Zip Code!"}
    elif len(auto_insurance.zipp.strip()) == 4:
        auto_insurance.zipp = "0" + auto_insurance.zipp.strip()

    try:
        components.proxyfy(auto_insurance.zipp, auto_insurance.city)
        add_to_sql.exec("queue", idd)
        add_to_sql.log(idd, "queue", "?")
    except Exception as e:
        add_to_sql.exec("errors", str(e))
        add_to_sql.log("errors", str(e), "x")
        raise HTTPException(status_code=404, detail=e)
        # raise HTTPException(status_code=400, detail="No proxies available for this zip code")

    return idd


@app.get('/download')
def download_full_csv():
    sql_to_csv("logs.csv", "SELECT * FROM log")
    return FileResponse('logs.csv', media_type='text/csv', filename=f'full_logs.csv')


@app.get('/download/{fromm}/{to}')
def download_as_csv(fromm, to):
    to = to if to != "0" else datetime.datetime.now().strftime("%Y-%m-%d")
    sql_to_csv("logs.csv", f"""SELECT * 
                                FROM log
                                where date >= '{fromm}'
                                AND date <= '{to}'""")
    return FileResponse('logs.csv', media_type='text/csv', filename=f'logs({fromm}>{to if to else "now"}).csv')


@app.delete('/delete/{id}')
def delete(id):
    con = sqlite3.connect('autoinsurance.db')
    cur = con.cursor()
    cur.execute(f"DELETE FROM queue WHERE id='{id}'")
    cur.execute(f"DELETE FROM log WHERE id='{id}'")
    con.commit()
    con.close()
    return "Deleted!"