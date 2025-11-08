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