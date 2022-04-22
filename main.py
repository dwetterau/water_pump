import airtable
from gpiozero import Robot
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import os
import time

def pump():
    # These numbers correspond to the pins we use on the Raspberry Pi.
    # Only 7/8 are configured for our single-pump setup, but we have to specify both
    r = Robot(left=(7, 8), right=(9, 10))
    try:
        r.backward(speed=1)
        # Run for five seconds.
        time.sleep(5)
    finally:
        r.stop()


def check_airtable():
    base_id = os.getenv("BASE_ID")
    api_key = os.getenv("API_KEY")
    table_name = os.getenv("TABLE_ID")
    at = airtable.Airtable(base_id, api_key)
    res = at.get(table_name)

    records = res["records"]
    pump_record = records[0]
    fields = pump_record["fields"]
    state = fields.get("State", "Idle")

    if state == "Pump":
        print("Commanded to pump. Starting...")
        pump()
        print("Done!")
        at.update(table_name, pump_record["id"], {"State": "Done"})

form_page = b"""
<html><form action=\"/\" method=\"POST\"><input type=\"submit\" value=\"Pump\"></form></body></html>
"""

class Handler(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request")
        self._set_response()
        self.wfile.write(form_page)

    def do_POST(self):
        logging.info("POST request")
        try:
            pump()
        except Exception:
            pass
        self._set_response()
        self.wfile.write(form_page)

def main():
    logging.basicConfig(level=logging.INFO)
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, Handler)
    logging.info('Starting server...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Server stopped.')

if __name__ == "__main__":
    main()
