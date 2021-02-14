
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
    'Led' : 1,
    'Color' : 2, 
    'Brightness' : 3, 
    'Speed' : 4, 
    'Scene' : 5
    }
    
    
    def __init__(self):
        self.bulps  = []
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
            self.bulps.append(tempBulp)
        
            #update this code later :  use a named list, and use the switchtype in that list
           
            if tempBulp.deviceId + self.UNITS['Led'] not in Devices:
                Domoticz.Device(Name='led ' + str(bulbNr)  , Unit=self.createUniqueUnitId(bulbNr, self.UNITS['Led']), TypeName="Switch", Image=0, Used=1).Create()
               

            if tempBulp.deviceId + self.UNITS['Color'] not in Devices:
                Domoticz.Device(Name= 'led ' + str(bulbNr)  + ' color', Unit=self.createUniqueUnitId(bulbNr, self.UNITS['Color']), TypeName="Switch", Image=0, Used=1).Create()
                
        
            if tempBulp.deviceId + self.UNITS['Brightness'] not in Devices:
                Domoticz.Device(Name= 'led '  + str(bulbNr)  +' brigthness ' , Unit=self.createUniqueUnitId(bulbNr, self.UNITS['Brightness']), TypeName="Switch", Image=0, Used=1).Create()
                
            if tempBulp.deviceId + self.UNITS['Speed'] not in Devices:
                Domoticz.Device(Name= 'led ' + str(bulbNr) + ' speed', Unit=self.createUniqueUnitId(bulbNr, self.UNITS['Speed']), TypeName="Switch", Image=0, Used=1).Create()
            

            if tempBulp.deviceId + self.UNITS['Scene'] not in Devices:
                Domoticz.Device(Name= 'led scene ' + str(bulbNr) + ' Scene' , Unit=self.createUniqueUnitId(bulbNr, self.UNITS['Scene']), TypeName="Switch", Image=0, Used=1).Create()
                

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
        Domoticz.Log("onCommand : onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        #find the bulp representing the unit
        bulbindex = self.getBulpIndexForUnitId(Unit)
        Domoticz.Log("bulb index calculated to : " + str(bulbindex))
        selectedBulb = self.bulps[bulbindex]
        if self.bulps[bulbindex] :
            selectedBulb = self.bulps[bulbindex]
            Domoticz.Log ("onCommand : Bulb found on calculated index")
            Domoticz.Log ("onCommand : issed command on bulb : " + str(self.bulps[bulbindex].model))
            
            # interprete command and send command to led strip now.
            unitsIndex = self.getUnitsDictKeyForUnitId(Unit)
            if self.UNITS['Led'] == unitsIndex :
                Domoticz.Log ("onCommand : received command for unittype  :  power switch")
                if Command=='Off':
                    selectedBulb.wifiLedBulp.turnOff()
                    Domoticz.Log ("onCommand : turning off device " +  Unit)
                    self.UpdateDomoticzDevice(Unit,0, "Off" )
                else :
                    selectedBulb.wifiLedBulp.turnOn()
                     Domoticz.Log ("onCommand : turning on device " +  Unit)
                    self.UpdateDomoticzDevice(Unit,0, "On" )

                

            elif self.UNITS['Color'] == unitsIndex : 
                Domoticz.Log ("onCommand : received command for unittype  : color switch")
            elif self.UNITS['Brightness'] == unitsIndex : 
                Domoticz.Log ("onCommand : received command for unittype  : Brightness switch")    
            elif self.UNITS['Speed'] == unitsIndex : 
                Domoticz.Log ("onCommand : received command for unittype  : Speed switch")    
            elif self.UNITS['Scene'] == unitsIndex : 
                Domoticz.Log ("onCommand : received command for unittype  : Scene switch")    

        else :
            Domoticz.Log("onCommand : ERR : Could not find bulb on wich command was issued")



    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called")
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
                if (bulb.wifiLedBulp.is_on):
                    self.UpdateDomoticzDevice(bulb.deviceId + self.UNITS['Led'] , 1, "On")
                    Domoticz.Log("updateDomoticzDeviceInfo - led power set to ON")
                else:   
                    #Devices[bulb.deviceId + self.UNITS['Led'] ].Update(0,"Off",5)
                    self.UpdateDomoticzDevice(bulb.deviceId + self.UNITS['Led'] , 0, "Off")
                    Domoticz.Log("updateDomoticzDeviceInfo - led power set to Off")
            else:
                Domoticz.log("updateDomoticzDeviceInfo -  ERR : it seems that the connection to the device is lost")
    
    def UpdateDomoticzDevice(self, unitId, nValue, sValue): 
        if unitId  in Devices:
            Devices[unitId].Update(nValue,sValue,5)
        else :
            Domoticz.Log("updateDomoticzDeviceInfo - ERR : device with unit id" + unitId + "not found in device list")


            
               

          





    


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


