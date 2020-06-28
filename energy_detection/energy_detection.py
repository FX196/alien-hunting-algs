import zmq
import pickle
import time
import os
import wget
from .. import upload

print("Running")

context = zmq.Context()
request_recv_socket = context.socket(zmq.PULL)
response_send_socket = context.socket(zmq.PUSH)
request_recv_socket.bind("tcp://*:5555")

print("Socket connected")

while True:
    serialized = socket.recv()
    request_dict = pickle.loads(serialized)
    data_url = request_dict["data_url"]
    response_addr = request_dict["response_addr"]

    print(f"Received request to process {data_url}")
    start = time.time()
    filename = wget.download(data_url)
    obs_name = os.path.splitext(filename)[0]
    print(f"Downloaded observation {obs_name}")
    fail = os.system(f"cd alien_hunting_algs/energy_detection && python3 preprocess_fine.py {os.path.join(os.getcwd(), filename)}")
    if fail:
        socket.send_string("Algorithm Failed")
        os.remove(filename)
        os.system(f"rm -rf {obs_name}")
        print(f"Algorithm Failed, removed {obs_name}")
        continue
    upload.upload_dir("bl-scale", os.path.join(obs_name))
    os.remove(filename)
    os.system(f"rm -rf {obs_name}")
    end = time.time()
    socket.send_string(
    f"Energy Detection and Result Upload finished in {end-start} seconds. Results uploaded to bl-scale/{obs_name}")
