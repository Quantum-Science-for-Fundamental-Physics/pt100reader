from Board import *
import Helper as api 
import json
import time

#OpAmp output Pin. Pin 26, 27, or 28.
ADC_PIN = 27

SELECT = [20, 19, 18]

#demuxes. Will be stored in an array. 
DEMUX_0 = 9
DEMUX_1 = 8
DEMUX_2 = 7
DEMUX_3 = 6
DEMUX_4 = 5
DEMUX_5 = 4

def main():

    DEMUXES = [DEMUX_0]
    tempSensors = controllerBoard(SELECT, DEMUXES, ADC_PIN)

    print(json.dumps({"status": "Pico ready"}))
    while True:
        msg = api.read_json_line()
        if not msg:
            time.sleep(0.05)
            continue

        cmd = msg.get("cmd", "").upper()
        tempSensors.handle(cmd)

if __name__ == "__main__":
    main()