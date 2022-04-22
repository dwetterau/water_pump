import os
import airtable

from gpiozero import Robot

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


def main():
    base_id = os.getenv("BASE_ID")
    api_key = os.getenv("API_KEY")
    table_name = os.getenv("TABLE_ID")
    at = airtable.Airtable(base_id, api_key)
    res = at.get(table_name)

    records = res["records"]
    pump = records[0]
    fields = pump["fields"]
    state = fields.get("State", "Idle")

    if state == "Pump":
        print("Commanded to pump. Starting...")
        pump()
        print("Done!")
        at.update(table_name, pump["id"], {"State": "Done"})

if __name__ == "__main__":
    main()
