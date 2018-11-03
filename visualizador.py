import os
import sys
import time
import uuid
import json
import logging
import argparse
from AWSIoTPythonSDK.core.greengrass.discovery.providers import DiscoveryInfoProvider
from AWSIoTPythonSDK.core.protocol.connection.cores import ProgressiveBackOffCore
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.exception.AWSIoTExceptions import DiscoveryInvalidRequestException

class Visualizador():
    
    MAX_DISCOVERY_RETRIES = 10
    GROUP_CA_PATH = "./groupCA/"


    def __init__(self,**kwargs):
    
        required_args = ["host","certificatePath","privateKeyPath","rootCAPath","thingName", "topic"]

        for attr_name in required_args:
            setattr(self, attr_name, kwargs[attr_name])

        self.clientId = self.thingName
        self.groupCA = ""

        self.configure_logger()


    def configure_logger(self):
        # Configure logging
        logger = logging.getLogger("AWSIoTPythonSDK.core")
        logger.setLevel(logging.DEBUG)
        streamHandler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        streamHandler.setFormatter(formatter)
        logger.addHandler(streamHandler)
        self.logger = logger

    
    def discover_core(self):

        # Progressive back off core
        backOffCore = ProgressiveBackOffCore()
        
        # Discover GGCs
        discoveryInfoProvider = DiscoveryInfoProvider()
        discoveryInfoProvider.configureEndpoint(self.host)
        discoveryInfoProvider.configureCredentials(self.rootCAPath, self.certificatePath, self.privateKeyPath)
        discoveryInfoProvider.configureTimeout(10)  # 10 sec
        
        retryCount = Visualizador.MAX_DISCOVERY_RETRIES
        discovered = False
        self.groupCA = None
        coreInfo = None
        while retryCount != 0:
            try:
                discoveryInfo = discoveryInfoProvider.discover(self.thingName)
                caList = discoveryInfo.getAllCas()
                coreList = discoveryInfo.getAllCores()
        
                # We only pick the first ca and core info
                groupId, ca = caList[0]
                coreInfo = coreList[0]
                print("Discovered GGC: %s from Group: %s" % (coreInfo.coreThingArn, groupId))
        
                print("Now we persist the connectivity/identity information...")
                self.groupCA = Visualizador.GROUP_CA_PATH + groupId + "_CA_" + str(uuid.uuid4()) + ".crt"
                if not os.path.exists(Visualizador.GROUP_CA_PATH):
                    os.makedirs(Visualizador.GROUP_CA_PATH)
                groupCAFile = open(self.groupCA, "w")
                groupCAFile.write(ca)
                groupCAFile.close()
        
                discovered = True
                print("Now proceed to the connecting flow...")
                break
            except DiscoveryInvalidRequestException as e:
                print("Invalid discovery request detected!")
                print("Type: %s" % str(type(e)))
                print("Error message: %s" % e.message)
                print("Stopping...")
                break
            except BaseException as e:
                print("Error in discovery!")
                print("Type: %s" % str(type(e)))
                print("Error message: %s" % e.message)
                retryCount -= 1
                print("\n%d/%d retries left\n" % (retryCount, Visualizador.MAX_DISCOVERY_RETRIES))
                print("Backing off...\n")
                backOffCore.backOff()
        
        if not discovered:
            print("Discovery failed after %d retries. Exiting...\n" % (Visualizador.MAX_DISCOVERY_RETRIES))
            sys.exit(-1)


    def loop(self,variable_to_update):
        
        self.discover_core()
        
        #import random
        #while True:
        #    variable_to_update[0] = random.randint(20,100)
        #    time.sleep(1)

        # General message notification callback
        def customOnMessage(message):
            print('Received message on topic %s: %s\n' % (message.topic, message.payload))
            variable_to_update[0] = message.payload

        # Iterate through all connection options for the core and use the first successful one
        myAWSIoTMQTTClient = AWSIoTMQTTClient(self.clientId)
        myAWSIoTMQTTClient.configureCredentials(self.groupCA, self.privateKeyPath, self.certificatePath)
        myAWSIoTMQTTClient.onMessage = customOnMessage
        
        connected = False
        for connectivityInfo in coreInfo.connectivityInfoList:
            currentHost = connectivityInfo.host
            currentPort = connectivityInfo.port
            print("Trying to connect to core at %s:%d" % (currentHost, currentPort))
            myAWSIoTMQTTClient.configureEndpoint(currentHost, currentPort)
            try:
                myAWSIoTMQTTClient.connect()
                connected = True
                break
            except BaseException as e:
                print("Error in connect!")
                print("Type: %s" % str(type(e)))
                print("Error message: %s" % e.message)
        
        if not connected:
            print("Cannot connect to core %s. Exiting..." % coreInfo.coreThingArn)
            sys.exit(-2)
        
        # Successfully connected to the core
        myAWSIoTMQTTClient.subscribe(self.topic, 0, None)
        
        while True:
            time.sleep(1)

    ## para conectarse coa plataforma
    def loopPlatform(self, variable_to_update):
        # General message notification callback
        def customOnMessage(message):
            print('Received message on topic %s: %s\n' % (message.topic, message.payload))
            variable_to_update[0] = message.payload

        myAWSIoTMQTTClient = AWSIoTMQTTClient(self.clientId)
        myAWSIoTMQTTClient.configureEndpoint(self.host, 8883)
        myAWSIoTMQTTClient.configureCredentials(self.rootCAPath, self.privateKeyPath, self.certificatePath)
        myAWSIoTMQTTClient.onMessage = customOnMessage

        # connect and subscribe to topic
        myAWSIoTMQTTClient.connect()
        myAWSIoTMQTTClient.subscribe(self.topic, 1, None)

        while True:
            time.sleep(1)




if __name__ == '__main__':

    v = Visualizador(
            privateKeyPath="./key", 
            certificatePath="./cert",
            host="",
            rootCAPath="",
            topic="",
            thingName=""
        )

    v.loop()


