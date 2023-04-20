# SaveOnAutoInsurance Automation Bot
Bot that automates the process of getting a quote from SaveOnAutoInsurance.com, with bot detection bypass.

## Features
- Bot detection bypass.
- Bot logs providing live updates on the status of the bot.
- Queue system to limit the number of running bots saving processing power and memory.
- Download logs to csv file from specified date.
- Set random page click percentage.

## End-points
- POST /add-to-queue - add bot to queue.
- GET / - set bot parameters.
- GET /logs - view bot logs.
- GET /logs/queue - view queued bots.
- GET /logs/success - view successful bots.
- GET /logs/success - view errors from bots or invalid inputs.
- GET /download - download bot logs to csv file.
- GET /download/{from}/{to} - download bot logs to csv file between specified dates.
- DELETE /delete/{id} - delete bot from queue.

## Installation
```bash
$ pip install -r requirements.txt
$ python -m playwright install
```

## run
```bash
$ uvicorn api:app
``` 