from Managers.BaseManager import BaseManager
from time import time
from Constants import *

class DeviceManager(BaseManager):
        
    def updateSensorReading(self, id, reading):
        sensor = self.getSensorById(id)
            
        if sensor == None:
            return False
            
        sensor["lastreading"] = reading
        sensor["lastupdated"] = int(time()) # Unix time.

        if sensor["alltimemax"] < reading:
            sensor["alltimemax"] = reading

        elif sensor["alltimemin"] > reading:
            sensor["alltimemin"] = reading

        sensors = self.parent.configManager.getConf(CONFIG_CORE).getItem("sensors", None)
        self.parent.configManager.getConf(CONFIG_CORE).setItem("sensors", sensors)
        return True
        
    def updateDeviceState(self, id, state):
        device = self.getDeviceById(id)
            
        if device == None:
            return False
        
        device["state"] = int(state)
        devices = self.parent.configManager.getConf(CONFIG_CORE).getItem("devices", None)
        self.parent.configManager.getConf(CONFIG_CORE).setItem("devices", devices)
        return True
    
    def createSensor(self, name, type, clientid, index):
        """
            Creates a new sensor object with the parameters supplied and assigns a new unique ID to it
            and then returns it. Use DeviceManager.insertSensor(sensor) to add the newly created sensor
            to the list.
        """
        
        sensor = {}
        sensor["name"] = name
        sensor["type"] = type
        sensor["index"] = index
        sensor["clientid"] = clientid
        sensor["lastreading"] = 0
        sensor["lastupdated"] = 0
        sensor["alltimemax"] = 0
        sensor["alltimemin"] = 0
        sensor["id"] = self.getNextId()
        
        return sensor
    
    def createDevice(self, name, type, clientid, index, maxontime, useshygrometer = False, hygrometerindex = -1):
        """
            Creates a new device object with the parameters supplied and assigns a new unique ID to it
            and then returns it. Use DeviceManager.insertDevice(device) to add the newly created device
            to the list.
        """
        
        device = {}
        device["name"] = name
        device["type"] = type
        device["index"] = index
        device["clientid"] = clientid
        device["state"] = 0
        device["maxontime"] = maxontime
        device["useshygrometer"] = useshygrometer
        device["hygrometerindex"] = hygrometerindex
        device["id"] = self.getNextId()
        
        return device
        
    def insertSensor(self, sensor, isStartup = False):
        if self.hasSensor(sensor["id"] and not isStartup):
            return '{"' + KEY_ERROR + '": ' + str(SENSOR_EXISTS_ERROR) + '}'
            
        response = self.parent.connection.send((sensor["clientid"], self.parent.protocol.insert(sensor, TYPE_SENSOR, isStartup)))

        if KEY_ERROR in response: return response
            
        if response[KEY_RESPONSE] == INSERT_SENSOR_SUCCESS and not isStartup:
            sensors = self.parent.configManager.getConf(CONFIG_CORE).getItem("sensors", None)
            sensors.append(sensor)
            self.parent.configManager.getConf(CONFIG_CORE).setItem("sensors", sensors)
        
        return response
        
    def insertDevice(self, device, isStartup = False):
        if self.hasDevice(device["id"] and not isStartup):
            return '{"' + KEY_ERROR + '": ' + str(PUMP_EXISTS_ERROR) + '}'
        
        response = {}
        
        if device["type"] == DEVICE_TYPE_PUMP:
            response = self.parent.connection.send((device["clientid"], self.parent.protocol.insert(device, TYPE_PUMP, isStartup)))
            
            if KEY_ERROR in response: return response
            if response[KEY_RESPONSE] != INSERT_PUMP_SUCCESS: return response
            
            if not isStartup:
                devices = self.parent.configManager.getConf(CONFIG_CORE).getItem("devices", None)
                devices.append(device)
                self.parent.configManager.getConf(CONFIG_CORE).setItem("devices", devices)
            
        return response
        
        return False
        
    def removeSensor(self, sensor):
        if not self.hasSensor(sensor["id"]):
            return '{"' + KEY_ERROR + '": ' + str(SENSOR_DOESNT_EXIST_ERROR) + '}'
            
        response = self.parent.connection.send((sensor["clientid"], self.parent.protocol.remove(sensor, TYPE_SENSOR)))
        
        if KEY_ERROR in response: return response
            
        sensors = self.parent.configManager.getConf(CONFIG_CORE).getItem("sensors", None)
        sensors.remove(sensor)
        self.parent.configManager.getConf(CONFIG_CORE).setItem("sensors", sensors)
        return response
    
    def removeSensorById(self, id):
        return self.removeSensor(self.getSensorById(id))
    
    def removeDevice(self, device):
        if not self.hasDevice(device["id"]):
            return '{"' + KEY_ERROR + '": ' + str(PUMP_DOESNT_EXIST_ERROR) + '}'
            
        response = self.parent.connection.send((device["clientid"], self.parent.protocol.remove(device, TYPE_PUMP)))
        
        if KEY_ERROR in response: return response
        
        devices = self.parent.configManager.getConf(CONFIG_CORE).getItem("devices", None)
        devices.remove(device)
        self.parent.configManager.getConf(CONFIG_CORE).setItem("devices", devices)
        return response
    
    def removeDeviceById(self, id):
        return self.removeDevice(self.getDeviceById(id))
        
    def getSensors(self):
        return self.parent.configManager.getConf(CONFIG_CORE).getItem("sensors", None)
    
    def getDevices(self):
        return self.parent.configManager.getConf(CONFIG_CORE).getItem("devices", None)
    
    def getSensorById(self, id):

        return self._getById("sensors", id)

    def getDeviceById(self, id):

        return self._getById("devices", id)

    def getSensorByName(self, name):

        return self._getByName("sensors", name)

    def getDevicesByName(self, name):

        return self._getByName("devices", name)

    def hasSensor(self, id):
        """
            Checks if the sensor list has a sensor with given unique ID.
        """

        return self._has("sensors", id)

    def hasDevice(self, id):
        """
            Checks if the device list has a device with given unique ID.
        """

        return self._has("devices", id)

    def hasSensorByName(self, name):
        """
            Checks if the sensor list has a sensor with given name. Largely needed when adding new sensors
            that don't yet have an ID assigned to them.
        """

        return self._hasByName("sensors", name)

    def hasDeviceByName(self, name):
        """
            Checks if the device list has a device with given name. Largely needed when adding new devices
            that don't yet have an ID assigned to them.
        """

        return self._hasByName("devices", name)