
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
    'Led',
    'Color', 
    'Brightness', 
    'Speed', 
    'Scene'
    }
    
    
    def __init__(self):
        self.bulps  = []
        return

    def onStart(self):
        Domoticz.Log("onStart called")
        #foundBulbs = Fluxled.BulbScanner().scan() #find all strips in the network
        scanner = BulbScanner()
        scanner.scan()
        bulb_info_list = scanner.getBulbInfo()
        
        # we have a list of buld info dicts
        addrs = []
        if options.scanresults and len(bulb_info_list) > 0 :
            for b in bulb_info_list:
                addrs.append(b['ipaddr'])
        else:
            print("{} bulbs found".format(len(bulb_info_list)))
            for b in bulb_info_list:
                print("  {} {}".format(b['id'], b['ipaddr']))

        if (len(bulb_info_list) > 0 ) :       
        #for all found strips    if Status == 0:
            for bulb in bulb_info_list :
                Domoticz.Log("bulb found with ip adress : " + bulb.ipaddr)
                tempBulp = MagicHome.DomoticzLedBulb(bulb.ipaddr,bulb.id , bulb_info_list[bulb]+bulb.id,  bulb.model)
                self.bulps.append(tempBulp)
            
                #update this code later :  use a named list, and use the switchtype in that list
            
                if bulb.deviceId + UNITS['Led'] not in Devices:
                    Domoticz.Device(Name= tempBulp.model, Unit=tempBulp.deviceId + UNITS['Led'], TypeName="Switch", Image=5, Used=1).Create()

                if bulb.deviceId + UNITS['Color'] not in Devices:
                    Domoticz.Device(Name= tempBulp.model, Unit=tempBulp.deviceId + UNITS['Color'], TypeName="Switch", Image=5, Used=1).Create()
            
                if bulb.deviceId + UNITS['Brightness'] not in Devices:
                    Domoticz.Device(Name= tempBulp.model, Unit=tempBulp.deviceId + UNITS['Brightness'], TypeName="Switch", Image=5, Used=1).Create()

                if bulb.deviceId + UNITS['Speed'] not in Devices:
                    Domoticz.Device(Name= tempBulp.model, Unit=tempBulp.deviceId + UNITS['Speed'], TypeName="Switch", Image=5, Used=1).Create()

                if bulb.deviceId + UNITS['Scene'] not in Devices:
                    Domoticz.Device(Name= tempBulp.model, Unit=tempBulp.deviceId + UNITS['Speed'], TypeName="Switch", Image=5, Used=1).Create()
        else:
            Domoticz.Log("No led strips found on the network")    


       
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
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called")

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


