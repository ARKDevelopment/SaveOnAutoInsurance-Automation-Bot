import csv, sqlite3, uuid, pandas
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse
from pydantic import BaseModel
from components import proxy_test, email_verified, log_html, percent_html


app = FastAPI()


conn = sqlite3.connect('autoinsurance.db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS queue (
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
                "Device",
                "Education",
                "Rating",
                "Status"
            ]
        )

        writer.writerows(cmd)

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


@app.get('/queued')
def queued():
    con = sqlite3.connect('autoinsurance.db')
    cur = con.cursor()
    cmd = cur.execute("SELECT * FROM queue")
    data = cmd.fetchall()
    # data_str = "<br/>".join(list(data))
    con.close()
    return data


@app.post('/add-to-queue')
async def automate(auto_insurance: AutoInsurance):
    if not email_verified(auto_insurance.email): 
        return "ERORR 400: Invalid Email!"
        # raise HTTPException(status_code=400, detail="Invalid email address")

    if len(auto_insurance.zipp.strip()) < 4 and len(auto_insurance.zipp.strip()) > 5:
        return {"ERORR 400": "Invalid Zip Code!"}
    elif len(auto_insurance.zipp.strip()) == 4:
        auto_insurance.zipp = "0" + auto_insurance.zipp.strip()
    # raise HTTPException(status_code=400, detail="Invalid Zip Code")    

    try:
        proxy_test(auto_insurance.city, auto_insurance.zipp)
    except Exception as e:
        return f"ERORR 400: {e}"
        # raise HTTPException(status_code=400, detail="No proxies available for this zip code")

    idd = str(uuid.uuid4())
    con = sqlite3.connect('autoinsurance.db')
    cur = con.cursor()
    cur.execute(f"""INSERT INTO queue (
    id, 
    first_name, 
    last_name, 
    street_address, 
    city, 
    zip, 
    phone, 
    email
    ) 
    VALUES ({"?, "*7}?)""", (
        idd,
        auto_insurance.first_name,
        auto_insurance.last_name,
        auto_insurance.street_address,
        auto_insurance.city,
        auto_insurance.zipp,
        auto_insurance.phone,
        auto_insurance.email))

    con.commit()
    con.close()
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
    con.commit()
    con.close()
    return "Deleted!"
