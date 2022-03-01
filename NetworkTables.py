# TE.AM ip: 10.5.40.2
# RoboRio mDNS: roboRIO-540-FRC.local

# 1. Connect to RoboRio network
# 2. Run 'ping roboRIO-540-FRC.local' in terminal
# 3. If it is successful then run this script, else troubleshoot

import time
import threading
from networktables import NetworkTableEntry, NetworkTables, NetworkTablesInstance, NetworkTable
from netifaces import interfaces, ifaddresses, AF_INET

serverCondition = threading.Condition() #Establish a Condition
rio_notified = [False]

# Wait for the Pi to establish a connect with the RoboRio so it doesnt pull null
# Do this by establishing a listener that will activate when the server is initialized

def connectionListener(connected, info):
    print(info, '; Connected=%s' % connected)
    with serverCondition:
        rio_notified[0] = True
        serverCondition.notify()

# Initalise client connection to the RoboRio server
NetworkTables.startClientTeam(540)
NetworkTables.initialize(server='10.5.40.2')
NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

# Check if we have initialized a connection to the RoboRio
# If we have, procced, if not then wait till we do
# This is also good because it doesnt allow us to send data to the Rio untill we have a connection (send a packet to Ayush's brain (nothing))

with serverCondition:
    print("Waiting for Server Connection")
    if not rio_notified[0]:
        serverCondition.wait()


# The Server has been Connected to so we can Procced with the Code

# Now lets wait for the Alliance color to be updated this is done by first:
# Checking if the pi is online by the Rio
# Then if it is lets wait for the pi to send the rio an online packet
# Once it recives the packet it will write to the table what the alliance color is
# We will then listen for that using another listener that will wait for that

# What needs to be tested:

# Get Local ip
def local_ip():
    for ifaceName in interfaces():
        addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
        if(' '.join(addresses) != 'No IP addr' ):
            if not(' '.join(addresses).startswith("127.")): # Local looping Subnet
                return(' '.join(addresses))

# Get Alliance color from Smart Dashboard
def getAlliacneColor():
    return(NetworkTables.getTable('SmartDashboard').getString('Alliance Color', False))


talonpi = NetworkTables.getTable('TalonPi')
talonpi.putString('Alliance Color','PIREADY')
allianceColor = talonpi.getAutoUpdateValue('Alliance Color','PIREADY')

while True:
    if not allianceColor.value == "PIREADY":
        print(allianceColor.value)
    # else:
    #     print("Pi is Awaiting Color")
    time.sleep(1)
    
# What needs to be added:
# Sending and Listening for Packet
# Reading from the Table