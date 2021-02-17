
"""
<plugin key="MagicHomePlugin" name="MagicHome" author="RubenCoppens" version="1.0.0" wikilink="http://www.domoticz.com/wiki/plugins/plugin.html" externallink="https://www.google.com/">
    <description>
        <h2>MagicHome</h2><br/>
        Overview...
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>Feature one...</li>
            <li>Feature two...</li>
        </ul>
        <h3>Devices</h3>
        <ul style="list-style-type:square">
            <li>Device Type - What it does...</li>
        </ul>
        <h3>Configuration</h3>
        Configuration options...
    </description>
   <param field="Address" label="IP Address" width="250px" required="true" default="192.168.1.238"/>
        <param field="Port" label="Port" width="50px" required="true" default="5577"/>
</plugin>
"""
import Domoticz
import MagicHome
import Fluxled

class BasePlugin:
   
    
    UNITS = {
    'Color' : 1, 
    'Speed' : 2, 
    'Scene' : 3
    }

    def __init__(self):
        self.bulps  = []
        self.hartbeats=0
        return

    def onStart(self):
        Domoticz.Log("onStart called")
        scanner = Fluxled.BulbScanner()
        scanner.scan(3,'')#find all strips in the network
        bulb_info_list = scanner.getBulbInfo()
    
       # Domoticz.Log("{} bulbs found".format(len(bulb_info_list)))
        for b in bulb_info_list:
            Domoticz.Log("  {} {}".format(b['id'], b['ipaddr']))
        # we have a list of buld info dicts
             
        #for all found strips    if Status == 0:
      
        bulbNr = 0
        
        for bulb in bulb_info_list :
            bulbNr +=1
        
            Domoticz.Log("bulb found with ip adress : " + bulb['ipaddr'])
            # TODO improve device id : now only based on index, and not on the device itself
            tempBulp = MagicHome.DomoticzLedBulb(bulb['ipaddr'],bulb['id'] , bulbNr * 100 ,  bulb['model'])
            tempBulp.wifiLedBulp.rgbwcapable = True
            self.bulps.append(tempBulp)
        
            #update this code later :  use a named list, and use the switchtype in that list
                          
            #TODO set color switch subtype according to supported led type
            if tempBulp.deviceId + self.UNITS['Color'] not in Devices: #241 type  = color switch ; subtype 7 = rgbwwz
                Domoticz.Device(Name= 'led ' + str(bulbNr)  + ' color', Unit=self.createUniqueUnitId(bulbNr, self.UNITS['Color']), TypeName="Color Switch ", Type=241, Subtype = 7,Switchtype = 7,  Image=0, Used=1).Create()
       
            if tempBulp.deviceId + self.UNITS['Speed'] not in Devices:
                Domoticz.Device(Name= 'led ' + str(bulbNr) + ' speed', Unit=self.createUniqueUnitId(bulbNr, self.UNITS['Speed']), TypeName="Dimmer", Image=0, Used=1).Create()
            

            if tempBulp.deviceId + self.UNITS['Scene'] not in Devices:
                Domoticz.Device(Name= 'led scene ' + str(bulbNr) + ' Scene' , Unit=self.createUniqueUnitId(bulbNr, self.UNITS['Scene']), TypeName="Input", Image=0, Used=1).Create()
                

        #self.SyncDevices(1)
        Domoticz.Heartbeat(30)

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")
        
        for bulb in self.bulps:
            if (Connection.Name == bulb.connection.Name):
                connectedBulp = bulb
                Domoticz.Debug("connection for led strip found")
                continue

        if (connectedBulp != None ):
            if Status == 0: # status from domoticz : connection succeed
                Domoticz.Debug("Connected successfully to: "+ Connection.Address +":"+ Connection.Port)
        
            else:
               # self.SyncDevices(1)
                Domoticz.Debug("Failed to connect ("+str(Status)+") to: " + connectedBulp.wifiLedBulp.ipaddr +" : " +connectedBulp.wifiLedBulp.port + " with error: "+Description)
        else:    
            Domoticz.Debug(str("Could not find connection in registered bulbs : { }" , Connection.Name))
        return

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand : onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level) +  " Hue : " + str(Hue))
        #find the bulp representing the unit
        #paramters / type of action
        #'On', Level: 100 Hue :
        #'Off', Level: 100 Hue 
        #set brightness : 'Set Level', Level: 61 Hue :
        #led Mode 3 : 'Set Color', Level: 100 Hue : {"b":77,"cw":0,"g":150,"m":3,"r":255,"t":0,"ww":0}
        #led Mode 2 : Set Color', Level: 100 Hue : {"b":0,"cw":48,"g":0,"m":2,"r":0,"t":207,"ww":207}
        #led Mode 4 : 'Set Color', Level: 100 Hue : {"b":153,"cw":127,"g":153,"m":4,"r":153,"t":128,"ww":128}
        # with level value and color in one command : 
        #'Set Color', Level: 78 Hue : {"b":0,"cw":134,"g":0,"m":2,"r":0,"t":121,"ww":121}

        bulbindex = self.getBulpIndexForUnitId(Unit)
        Domoticz.Log("bulb index calculated to : " + str(bulbindex))
        if self.bulps[bulbindex] :
            selectedBulb = self.bulps[bulbindex]
            Domoticz.Log ("onCommand : Bulb found on calculated index")
            Domoticz.Log ("onCommand : issed command on bulb : " + str(self.bulps[bulbindex].model))
            
            # interprete command and send command to led strip now.
            unitsIndex = self.getUnitsDictKeyForUnitId(Unit)
            #Power logic
            if self.UNITS['Color'] == unitsIndex :
                Domoticz.Log ("onCommand : received command for unittype  :  color light")
                if Command=='Off':
                    selectedBulb.wifiLedBulp.turnOff()
                    Domoticz.Log ("onCommand : turning off device " +  str("Unit"))
                    self.UpdateDomoticzDevice(Unit,0, "Off" )
                elif Command == 'On' :
                    selectedBulb.wifiLedBulp.turnOn()
                    Domoticz.Log ("onCommand : turning on device " +  str("Unit"))
                    self.UpdateDomoticzDevice(Unit,0, "On" )
                elif Command == 'Set Level' :
                    #This still contains a bug.. need a fix!
                    rgbww = None
                    #(red, green, blue, white, white2)
                    rgbww = selectedBulb.wifiLedBulp.getRgbww()  
                    # self, r=None, g=None, b=None, w=None, persist=True,
                    # brightness=None,9 retry=2, w2=None):
                    bright = (Level * 255 )/ 100 #from % to a value on a scale of 255/
                    Domoticz.Log ("onCommand : setting brightness to " + str(int(bright)) + " For device " +  str(Unit) + " rgb :" + str(rgbww[0]) + " : " +str(rgbww[1]) + " : " + str(rgbww[2]) + " : " + str(rgbww[3]))
                    selectedBulb.wifiLedBulp.setRgbw(rgbww[0],rgbww[1],rgbww[2], True, int(bright) , 2, rgbww[3])     
                elif Command == 'Set Color' :
                    # brightness=None, retry=2, w2=None):
                    bright = (Level * 255 )/ 100 #from % to a value on a scale of 255
                    #translate mode from Domoticz to FluxLed
                    #Level: 78 Hue : {"b":0,"cw":134,"g":0,"m":2,"r":0,"t":121,"ww":121}
                    if Hue[3] == 2 :
                        Domoticz.Log("onCommand - WW mode")
                        #level, persist=True, retry=2):
                        selectedBulb.wifiLedBulp.setWarmWhite(int(Hue[6]))
                        selectedBulb.wifiLedBulp.setColdWhite(int(Hue[1]))
                    #read out hue values

                    #call fluxled with values

                    #maybe : update Domoticz device with new values
                    elif Hue[3] == 3:
                        Domoticz.Log("onCommand - RGB mode")
                        # 'Set Color', Level: 100 Hue : {"b":77,"cw":0,"g":150,"m":3,"r":255,"t":0,"ww":0}
                        #(r,g,b, persist=True, brightness=None, retry=2):
                        selectedBulb.wifiLedBulp.setRgb(r = Hue[4],g = Hue[2],b = Hue[0],brightness=None)
                    elif Hue[3] == 4:
                        Domoticz.Log("onCommand - RGBWW mode")
                        #r=None, g=None, b=None, w=None, persist=True,brightness=None, retry=2, w2=None):
                        selectedBulb.wifiLedBulp.setRgbw(r = Hue[4],g = Hue[2],b = Hue[0],w=Hue[1] ,brightness=None, w2=Hue[6])

                else :
                    Domoticz.Log("onCommand : command not implemented yet ")
                        
                       
            #Color Switch logic
            
            elif self.UNITS['Speed'] == unitsIndex : 
                Domoticz.Log ("onCommand : received command for unittype  : Speed switch")    
            elif self.UNITS['Scene'] == unitsIndex : 
                Domoticz.Log ("onCommand : received command for unittype  : Scene switch")   

            selectedBulb.wifiLedBulp.update_state() 
        else :
            Domoticz.Log("onCommand : ERR : Could not find bulb on wich command was issued")



    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")
        for bulb in self.bulps:
            bulb.wifiLedBulp.close()

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called")
        self.hartbeats +=1
        if (len(self.bulps) > 0):
            self.updateAllDomoticzDeviceInfo()
            
            

    def DumpInfoInLog(self, bulp):
        connectionInfo =bulp.connectionFailed
        isOn = bulp.getWifiLedBulp().isOn()
        Domoticz.Log("DumpInfoInLog - current state info on led : id : "+ bulp.getBulpId() + "  - connectionFailed: " + str(connectionInfo) +" - isOn : " + str(isOn))
    
    def createUniqueUnitId(self,deviceId, unitIndex ): #seems stupid function, but it's not
         return deviceId * 100 + unitIndex #make a unique number. restriction of domoticz, you cannot have more then 255 leds in one hardware

    def getBulpIndexForUnitId(self, Unit):
        return int(Unit / 100 ) - 1 # the result will be a double, but to find the right ID, we need only the first natural part
        #as in array index starts at 0 (-1 is needed)
    
    def getUnitsDictKeyForUnitId(self, Unit):
        unitIndex = Unit % 100 
        Domoticz.Log ("getUnitsDictKeyForUnitId - calculated dict key : " + str(unitIndex ))
        #if  unitIndex in self.UNITS  : 
        return unitIndex
        #else:
        #    Domoticz.Log("getUnitsDictKeyForUnitId -  ERROR")

    
    def updateAllDomoticzDeviceInfo(self):
        for bulb in self.bulps:
            self.DumpInfoInLog(bulb)
            if bulb.connectionFailed != True:
                Domoticz.Log("updateDomoticzDeviceInfo - led power device found")
                # method signature : Devices[Unit].Update(nValue=nValue, sValue=str(sValue), TimedOut=TimedOut)
                if self.hartbeats >=3 : #update led state after 3 hartbeats ; TODO make this configurable
                    bulb.wifiLedBulp.update_state
                    self.hartbeats = 0 # reset
                #Update power
                if (bulb.wifiLedBulp.is_on):
                    self.UpdateDomoticzDevice(bulb.deviceId + self.UNITS['Color'] , 1, "On")
                    Domoticz.Log("updateDomoticzDeviceInfo - led power set to ON")
                    #update color   
                    # self.mode = "ww"
                    #self.warmth_level = utils.percentToByte(level)
                    #self.pattern_code = 0x61
                    #self.red = 0
                    #self.green = 0
                    #self.blue = 0
                    #self.turn_on = True

                    #ColorMode {
                    #ColorModeNone = 0,   // Illegal
                    #ColorModeWhite = 1,  // White. Valid fields: none
                    #ColorModeTemp = 2,   // White with color temperature. Valid fields: t
                    #ColorModeRGB = 3,    // Color. Valid fields: r, g, b.
                    #ColorModeCustom = 4, // Custom (color + white). Valid fields: r, g, b, cw, ww, depending on device capabilities
                    #ColorModeLast = ColorModeCustom,
            
        
                    clor = None 
                    rgb  = bulb.wifiLedBulp.getRgbww()
                    clor = self.createColorJsonObj (bulb.m,bulb.wifiLedBulp.getWarmWhite255,rgb[0],rgb[1],rgb[2],rgb[3],rgb[4])

                    if( clor != None):
                        Domoticz.Log("updateAllDomoticzDeviceInfo - incoming led brightness :" + str(bulb.wifiLedBulp.brightness))
                        brightnessInPercent = (bulb.wifiLedBulp.brightness /255) * 100
                        Domoticz.Log("updateAllDomoticzDeviceInfo - Bightness level : " + str(int(brightnessInPercent ))+ "%")
                        Devices[bulb.deviceId + self.UNITS['Color']].Update(nValue=1, sValue=str(int(brightnessInPercent)),Color = clor )
                    else:
                        Domoticz.Log("updateAllDomoticzDeviceInfo - ERR unimplemented color mode")

                else:   
                    #Devices[bulb.deviceId + self.UNITS['Led'] ].Update(0,"Off",5)
                    self.UpdateDomoticzDevice(bulb.deviceId + self.UNITS['Color'] , 0, "Off")
                    Domoticz.Log("updateDomoticzDeviceInfo - led power set to Off")
            else:
                Domoticz.log("updateDomoticzDeviceInfo -  ERR : it seems that the connection to the device is lost")
    
    def UpdateDomoticzDevice(self, unitId, nValue, sValue): 
        if unitId  in Devices:
            Devices[unitId].Update(nValue,sValue,5)
        else :
            Domoticz.Log("updateDomoticzDeviceInfo - ERR : device with unit id" + unitId + "not found in device list")

    def createColorJsonObj(self,m, t, r,g,b,cw,ww ):
       

        if m == "ColorModeWhite" :
          return """ColorMode { \ 
           	ColorModeNone = 0,   // Illegal
           	ColorModeWhite = 1,  // White. Valid fields: none
           	ColorModeTemp = 2,   // White with color temperature. Valid fields: t
           	ColorModeRGB = 3,    // Color. Valid fields: r, g, b.
           	ColorModeCustom = 4, // Custom (color + white). Valid fields: r, g, b, cw, ww, depending on device capabilities
           	ColorModeLast = ColorModeCustom,
           };
           
           Color {
           	ColorMode""" + str(1) + """;
            }"""

        if m == "ColorModeTemp" :
          return """ColorMode { \ 
           	ColorModeNone = 0,   // Illegal
           	ColorModeWhite = 1,  // White. Valid fields: none
           	ColorModeTemp = 2,   // White with color temperature. Valid fields: t
           	ColorModeRGB = 3,    // Color. Valid fields: r, g, b.
           	ColorModeCustom = 4, // Custom (color + white). Valid fields: r, g, b, cw, ww, depending on device capabilities
           	ColorModeLast = ColorModeCustom,
           };
           
           Color {
           	ColorMode""" + str(2) + """;
           	uint8_t """ + str(t) + """;     // Range:0..255, Color temperature (warm / cold ratio, 0 is coldest, 255 is warmest)
           }"""

        if m == "ColorModeRGB" :
          return """ColorMode { \ 
           	ColorModeNone = 0,   // Illegal
           	ColorModeWhite = 1,  // White. Valid fields: none
           	ColorModeTemp = 2,   // White with color temperature. Valid fields: t
           	ColorModeRGB = 3,    // Color. Valid fields: r, g, b.
           	ColorModeCustom = 4, // Custom (color + white). Valid fields: r, g, b, cw, ww, depending on device capabilities
           	ColorModeLast = ColorModeCustom,
           };
           
           Color {
           	ColorMode""" + str(3) + """;
           	uint8_t """ + str(r) + """;     // Range:0..255, Red level
           	uint8_t """ + str(g) + """;     // Range:0..255, Green level
           	uint8_t """ + str(b) + """;     // Range:0..255, Blue level
           }"""

        if m == "ColorModeCustom" :
          return """ColorMode { \ 
           	ColorModeNone = 0,   // Illegal
           	ColorModeWhite = 1,  // White. Valid fields: none
           	ColorModeTemp = 2,   // White with color temperature. Valid fields: t
           	ColorModeRGB = 3,    // Color. Valid fields: r, g, b.
           	ColorModeCustom = 4, // Custom (color + white). Valid fields: r, g, b, cw, ww, depending on device capabilities
           	ColorModeLast = ColorModeCustom,
           };
           
           Color {
           	ColorMode""" + str(4) + """;
           	uint8_t """ + str(t) + """;     // Range:0..255, Color temperature (warm / cold ratio, 0 is coldest, 255 is warmest)
           	uint8_t """ + str(r) + """;     // Range:0..255, Red level
           	uint8_t """ + str(g) + """;     // Range:0..255, Green level
           	uint8_t """ + str(b) + """;     // Range:0..255, Blue level
           	uint8_t """ + str(cw) + """;    // Range:0..255, Cold white level
           	uint8_t """ + str(ww) + """;    // Range:0..255, Warm white level (also used as level for monochrome white)
           }"""

        


            
               

          





    


global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()


