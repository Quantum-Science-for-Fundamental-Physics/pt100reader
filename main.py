from machine import ADC, Pin
import utime

#OpAmp output Pin. Pin 26, 27, or 28.
ADC_PIN = 26

SELECT = [11, 12, 13]

#demuxes. Will be stored in an array. 
DEMUX_0 = 10
#DEMUX_1 = 
#DEMUX_2 = 
#DEMUX_3 =
#DEMUX_4 =
#DEMUX_5 =

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

        #Temp sensors are selected by commanding E, A, B, C. 

        self.sensorAddress = []
        for i in range(len(self.__demuxes)):
            for j in range(8):
                self.sensorAddress.append([i, j])

    def select_demux(self, demux_index):
        
        #Make sure no demux is active before activating one
        for demux in self.__demuxes:
            demux.value(0)
        
        self.__demuxes[demux_index].value(1)
    
    def select_channel(self, channel):
        """
        Select a channel (0–7) on the active demux.
        demux_index: which demux in self.demuxes to control
        channel: int 0–7 (binary determines selector pin states)
        """
        if not (0 <= channel <= 7):
            raise ValueError("Channel must be 0–7")

        # Write each bit of the channel number to the corresponding pin
        for i in range(3):  # 3 selector bits
            bit_val = (channel >> i) & 1
            self.__select[i].value(bit_val)
    
    def read_value(self):
        return self.__adcPin.read_u16()
    

    def __getitem__(self, index):

        #Select correct demux
        self.select_demux(self.sensorAddress[index % 7][0])

        #Select correct channel
        self.select_channel(self.sensorAddress[index][1])

        #Wait for voltage to stabilize
        utime.sleep(1)

        #Read input
        input = self.read_value()

        print(f"input read: temp sensor #{index}")
              
        return input

def main():
    print("Hello world from pico 2!")
    DEMUXES = [DEMUX_0]

    tempSensors = controllerBoard(SELECT, DEMUXES, ADC_PIN)

    i = 0
    while(True):
        print(f"Input Value: {tempSensors[i]}")
        i += 1
        i = i % 7

if __name__ == "__main__":
    main()