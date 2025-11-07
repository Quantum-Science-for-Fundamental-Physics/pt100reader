from BoardController import *
import sys
import time
import json
import select

def read_json_line():
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline().strip()
        if not line:
            return None
        try:
            return json.loads(line)
        except ValueError:
            print(json.dumps({"error": "Invalid JSON"}))
    return None

def main():

    DEMUXES = [DEMUX_0]
    tempSensors = controllerBoard(SELECT, DEMUXES, ADC_PIN)

    print(json.dumps({"status": "Pico ready"}))
    while True:
        msg = read_json_line()
        if not msg:
            time.sleep(0.05)
            continue

        cmd = msg.get("cmd", "").upper()
        if cmd == "PING":
            print(json.dumps({"resp": "PONG"}))
        elif cmd == "TEMP":
            print(json.dumps({"resp": "TEMP", "value": tempSensors[0]}))
        else:
            print(json.dumps({"error": f"Unknown cmd: {cmd}"}))

if __name__ == "__main__":
    main()