#!/usr/bin/env python3
import time
from openpilot.common.params import Params

import socket
import cereal.messaging as messaging
from cereal.services import SERVICE_LIST

def server_logic(host='0.0.0.0', port=8888):
  sm = messaging.SubMaster(['carState'])
  # Assumes V2VData is defined in cereal/log.capnp
  v2v_dat = messaging.new_message('v2vData')

  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    s.listen()
    print(f"Server listening on {host}:{port}")
    conn, addr = s.accept()
    with conn:
      print(f"Connected by {addr}")
      while True:
        sm.update()
        if sm.updated['carState']:
          # 1. Get lead vehicle speed and acceleration
          v_ego = sm['carState'].vEgo
          a_ego = sm['carState'].aEgo

          # 2. Pack into V2VData message
          v2v_dat.v2vData.vLead = v_ego
          v2v_dat.v2vData.aLead = a_ego

          # 3. Serialize and send over TCP
          try:
            conn.sendall(v2v_dat.to_bytes())
          except (BrokenPipeError, ConnectionResetError):
            print("Client disconnected. Waiting for new connection.")
            conn, addr = s.accept() # Wait for a new client
            print(f"Reconnected by {addr}")

        # Run at 10Hz
        time.sleep(0.1)

def client_logic(host='192.168.43.1', port=8888): # NOTE: Use the actual IP of the host vehicle
  pm = messaging.PubMaster(['carState'])

  while True:
    try:
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"Attempting to connect to {host}:{port}...")
        s.connect((host, port))
        print("Connected to host.")
        while True:
          # 1. Listen for incoming data
          data = s.recv(4096) # Adjust buffer size as needed
          if not data:
            break

          # 2. Parse back into V2VData and publish locally
          v2v_dat = messaging.new_message('v2vData').from_bytes(data)
          pm.send('v2vData', v2v_dat)

    except (ConnectionRefusedError, TimeoutError, OSError) as e:
      print(f"Connection failed: {e}. Retrying in 5 seconds...")
      time.sleep(5)

def main():
    params = Params()
    role = params.get("V2VRole", encoding='utf-8') # V2VRole should be 'host' or 'client'

    if role == "host":
        server_logic()
        # print("Starting in HOST mode.")
    elif role == "client":
      client_logic()
        # print("Starting in CLIENT mode.")
    else:
        print(f"Invalid V2VRole: '{role}'. Exiting.")
        return

    while True:
        # The respective logic function will handle the loop
        time.sleep(1)

if __name__ == "__main__":
    main()
