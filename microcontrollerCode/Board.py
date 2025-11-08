from machine import ADC, Pin
import Helper
import utime
import math
import json

CHANNELS = 8
MEASUREMENTS_PER_MEASUREMENT = 75

class controllerBoard:
    def __init__(self, select, demuxes, adcPin):
        #Addresses=which pins to look for a dmux
        #adcPin=which pin we read the input from

        self.__adcPin = ADC(Pin(adcPin))
        self.__select = []
        for s in select:
            self.__select.append(Pin(s, Pin.OUT))

        self.__demuxes = []
        for demux in demuxes:
            self.__demuxes.append(Pin(demux, Pin.OUT))
        
        self.__current_channel = 0
        self.__current_demux = 0

    def select_demux(self, demux_index):
        
        #Make sure no demux is active before activating one
        for demux in self.__demuxes:
            demux.value(1)
        #print(f"Demux {demux_index} selected.")
        self.__demuxes[demux_index].value(0)
        self.__current_demux = demux_index
    
    def select_channel(self, channel):
        """
        Select a channel (0–7) on the active demux.
        demux_index: which demux in self.demuxes to control
        channel: int 0–7 (binary determines selector pin states)
        """
        if not (0 <= channel <= 7):
            raise ValueError("Channel must be 0–7")

        #print(f"Channel {channel} selected")

        # Write each bit of the channel number to the corresponding pin
        for i in range(3):  # 3 selector bits
            bit_val = (channel >> i) & 1
            self.__select[i].value(bit_val)

        self.__current_channel = channel

        #print(f"{self.__select[0].value()}{self.__select[1].value()}{self.__select[2].value()}")


    def read_value(self):
        return self.__adcPin.read_u16()
    
    def take_measurement(self):
        temps = 0
        for i in range(MEASUREMENTS_PER_MEASUREMENT):
            temps += self.read_value()
        return temps / MEASUREMENTS_PER_MEASUREMENT

    def __getitem__(self, index):

        #Select correct demux
        self.select_demux(math.floor(index / CHANNELS))

        #Select correct channel
        self.select_channel(index % CHANNELS)

        #Wait for voltage to stabilize
        utime.sleep(0.01)

        #Read input
        input = self.take_measurement()

        #print(f"Reading temp sensor #{index}.")
        #print(f"On Demux: {self.__demuxes[math.floor(index / 8)]}")
              
        return input
    
    def __iter__(self):
        for demux in range(len(self.__demuxes)):
            self.select_demux(demux)
            for channel in range(CHANNELS):
                self.select_channel(channel)
                yield self.take_measurement()

    def getTemps(self):
        temps = []
        for temp in self:
            temps.append(temp)
        return temps
    
    def tempIncrement(self):
        self.select_channel(self.__current_channel)
        self.__current_channel += 1
        if self.__current_channel >= 8:
            self.__current_channel = 0

    def handle(self, cmd):
        if cmd == "PING":
            print(json.dumps({"resp": "PONG"}))
        elif cmd == "TEMPS":
            print(json.dumps({"resp": "TEMPS", "temp_values": self.getTemps()}))
        elif cmd == "STEP":
            print(json.dumps({"resp": f"Channel: {self.__current_channel}", "value": self.tempIncrement()}))
        else:
            print(json.dumps({"error": f"Unknown cmd: {cmd}"}))