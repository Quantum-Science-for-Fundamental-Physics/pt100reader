from machine import ADC, Pin
import utime
import math

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

    def select_demux(self, demux_index):
        
        #Make sure no demux is active before activating one
        for demux in self.__demuxes:
            demux.value(1)
        #print(f"Demux {demux_index} selected.")
        self.__demuxes[demux_index].value(0)
    
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

        #print(f"{self.__select[0].value()}{self.__select[1].value()}{self.__select[2].value()}")


    def read_value(self):
        return self.__adcPin.read_u16()
    
    def take_measurement(self):
        temps = 0
        for i in range(100):
            temps += self.read_value()
        return temps / 100

    def __getitem__(self, index):

        #Select correct demux
        self.select_demux(math.floor(index / 8))

        #Select correct channel
        self.select_channel(index % 8)

        #Wait for voltage to stabilize
        utime.sleep(0.5)

        #Read input
        input = self.take_measurement()

        #print(f"Reading temp sensor #{index}.")
        #print(f"On Demux: {self.__demuxes[math.floor(index / 8)]}")
              
        return input