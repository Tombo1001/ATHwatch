import subprocess
from datetime import datetime
import requests
import sys
import os
import json
from time import sleep
from coinbase.wallet.client import Client
from influxdb import InfluxDBClient
import psycopg2
import argparse
from pycoingecko import CoinGeckoAPI

print("ATHwatch container started and running...")
InfluxDB_IP = os.environ['INFLUXDB_IP']
InfluxDB_port = os.environ['INFLUXDB_PORT']
InfluxDB_name = os.environ['INFLUXDB_NAME']
print("Environment variables loaded:")
print(f"InfluxDB IP Address: {InfluxDB_IP}")
print(f"InfluxDB Port: {InfluxDB_port}")
print(f"InfluxDB DB Name: {InfluxDB_name}")

debug = False
cg = CoinGeckoAPI()

def func_get_cgdata(coin, athtemp):
    fiat = "usd"
    athvalue = athtemp
    try:
        mcap = cg.get_price(ids=coin, vs_currencies=fiat, include_market_cap='true')
        cvalue = float(mcap[coin][fiat])
        if cvalue > athtemp:
            athtemp = cvalue
            print("New ATH reached: $" + str(mcap[coin][fiat]))
            return(athtemp)
        else:
            return(athvalue)
    except:
        print("Error getting market cap from Coingecko")


def func_log_ath(coin, value):
    InfluxDB_IP = os.environ['INFLUXDB_IP']
    InfluxDB_name = os.environ['INFLUXDB_NAME']
    InfluxDB_port = os.environ['INFLUXDB_PORT']
    client = InfluxDBClient(host=InfluxDB_IP, port=InfluxDB_port)
    client.switch_database(InfluxDB_name)

    json_body = [
        {
            "measurement": "ATH",
            "tags": {
                "coin": f'{coin}'
            },
            "fields": {
                "value": value
            },
            "time": f'{datetime.utcnow().isoformat()}Z'
        }
    ]

    try:
        if client.write_points(json_body):
            # do nothing
            success = True
        else:
            print("ERROR writing to InfluxDB")
    except:
        print("ERROR writing to InfluxDB")


def func_cg_get_price():
    try:
        pgdb_IP= os.environ['PGDB_IP']
        pgdb_PORT= os.environ['PGDB_PORT']
        pgdb_USER= os.environ['PGDB_USER']
        pgdb_PASS= os.environ['PGDB_PASS']
        pgdb_NAME= os.environ['PGDB_NAME']
        con = psycopg2.connect(database=pgdb_NAME, user=pgdb_USER, password=pgdb_PASS, host=pgdb_IP, port=pgdb_PORT)
        cur = con.cursor()
        cur.execute("SELECT coin, athvalue, cgname from ath")
        rows = cur.fetchall()

        for row in rows:
            coinsymbol = row[0]
            ath = float(row[1])
            cgcoinname = row[2]
            print(f"From DB - Coin: {coinsymbol}, ATH: ${str(ath)}, CoinGecko ID: {cgcoinname}")
            athvalue = func_get_cgdata(cgcoinname, ath)
            updatequery = (f"UPDATE ath SET athvalue={float(athvalue)} WHERE coin='{coinsymbol}';")
            cur.execute(updatequery)
            con.commit()
            func_log_ath(coinsymbol, athvalue) #upate influxdb ATH value
    except:
        print("Unable to connect to PostgreSQL")


def main(argv):
    global debug
    global athvalue
    global ethathvalue
    global btcathvalue
    global atomathvalue
    global coins
    pgwritecounter = 0


    parser = argparse.ArgumentParser(prog='python ATHwatch.py', description='Watch your crypto moon from the safety of your Lambo')
    parser.add_argument('-d', '--debug', required=False, help='Set Debug Mode for Local Dev', action='store_true')
    args = parser.parse_args()

    if args.debug:
        debug = True

    while True:
        if not debug:
            func_cg_get_price()
        else:
            print("You are in debug mode.")
            if pgwritecounter >= 600: #10 minutes
                print("time to write DB")
                pgwritecounter = 0 #reset couunter after write
            print(f"Seconds since last PG write: {pgwritecounter}")
            pgwritecounter = pgwritecounter + 120
            func_cg_get_price()
        sleep(120)

if __name__ == '__main__':
    main(sys.argv)