import os
import airtable

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
        # TODO: Start pumping async...
        print("Done!")
        at.update(table_name, pump["id"], {"State": "Done"})

if __name__ == "__main__":
    main()
