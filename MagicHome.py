import Domoticz
import Fluxled

class DomoticzLedBulb: 
   
    def __init__ (self,  ipaddr, bulpId ,  deviceId, model ):
    
        self.bulpId = bulpId
        self.deviceId =deviceId
        self.model = model  
        self.connectionFailed=False  
        self.m = None
        DomoticzLedBulb.enableDomoticzOnConnect(self,ipaddr, "5577") # the wifibulpclass makes its own connections, by listing on the ip and port.. 
        try:
            self.wifiLedBulp = Fluxled.WifiLedBulb(ipaddr) #during init of the class, a connection is made aswell
            
            #to Domoticz own colormode
            if self.wifiLedBulp.mode =="ww" :
                self.m = "ColorModeTemp"
            elif self.wifiLedBulp.mode == "color":
                self.m="ColorModeRGB"
            elif self.wifiLedBulp.mode == "custom":
                self.m="ColorModeCustom"

        except Exception as e:
            Domoticz.Log("Unable to connect to bulb at [{}]: {}".format(ipaddr,e))
            self.connectionFailed=True
            

    def getDeviceId(self):
        return self.deviceId

    def getBulpId(self):
        return self.bulpId

    def getWifiLedBulp(self):
        return self.wifiLedBulp

    def enableDomoticzOnConnect(self, ipaddr, port):
        self.connection = Domoticz.Connection(Name="conn"+self.model, Transport="TCP/IP", Protocol="ICMP", Address=ipaddr, Port=port)
        self.connection.Listen()



   

