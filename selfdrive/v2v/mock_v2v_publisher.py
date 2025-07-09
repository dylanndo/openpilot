#!/usr/bin/env python3
import time
import math
import cereal.messaging as messaging
from openpilot.common.realtime import Ratekeeper

def mock_publisher():
    pm = messaging.PubMaster(['carState'])
    rk = Ratekeeper(10.0) # Publish at 10Hz, same as the real server

    # Create a fake data message
    v2v_dat = messaging.new_message('v2vData')
    counter = 0

    print("Starting mock V2V publisher...")
    while True:
        # Create some fake, dynamic data
        v2v_dat.v2vData.vLead = 20.0 + 5.0 * math.sin(counter * 0.1) # Speed oscillates
        v2v_dat.v2vData.aLead = 0.5 * math.cos(counter * 0.1)      # Acceleration oscillates

        # Publish the message
        pm.send('v2vData', v2v_dat)
        print(f"Published mock data: vLead={v2v_dat.v2vData.vLead:.2f}, aLead={v2v_dat.v2vData.aLead:.2f}")

        counter += 1
        rk.keep_time()

if __name__ == "__main__":
    mock_publisher()
