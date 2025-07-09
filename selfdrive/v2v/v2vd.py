#!/usr/bin/env python3
import time
from openpilot.common.params import Params

def main():
    params = Params()
    role = params.get("V2VRole", encoding='utf-8') # V2VRole should be 'host' or 'client'

    if role == "host":
        # server_logic()
        print("Starting in HOST mode.")
    elif role == "client":
      # client_logic()
        print("Starting in CLIENT mode.")
    else:
        print(f"Invalid V2VRole: '{role}'. Exiting.")
        return

    while True:
        # The respective logic function will handle the loop
        time.sleep(1)

if __name__ == "__main__":
    main()
