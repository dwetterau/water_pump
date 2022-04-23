import airtable
from gpiozero import Robot
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import os
import time

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
<html>
<head>
<style>
input[type="submit"]{
    width: 100%;
    height: 100%;
    font-size: xxx-large;
}
</style>
</head>
<body>
<form action=\"/\" method=\"POST\"><input type=\"submit\" value=\"Start / Stop Pump\"></form>
</body>
</html>
"""

class Handler(BaseHTTPRequestHandler):
    pumping = False
    robot = None
    def pump(self):
        # These numbers correspond to the pins we use on the Raspberry Pi.
        # Only 7/8 are configured for our single-pump setup, but we have to specify both
        if not self.robot:
            self.robot = Robot(left=(7, 8), right=(9, 10))
        if not self.pumping:
            self.pumping = True
            self.robot.backward(speed=1)
        else:
            self.robot.stop()
            self.pumping = False

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request")
        self._set_response()
        self.wfile.write(form_page)

    def do_POST(self):
        try:
            self.pump()
        except Exception as e:
            print("error encountered: {}".format(e))
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
