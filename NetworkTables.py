# TE.AM ip: 10.5.40.2
# RoboRio Local ip: roboRIO-540-FRC.local

# 1. Connect to RoboRio network
# 2. Run 'ping roboRIO-540-FRC.local' in terminal
# 3. If it is successful then run this script, else troubleshoot

import threading
from networktables import NetworkTables

serverCondition = threading.Condition() #Establish a Condition
rio_notified = False

# Wait for the Pi to establish a connect with the RoboRio so it doesnt pull null
# Do this by establishing a listener that will activate when the server is initialized

def connectionListener(connected, info):
    print(info, '; Connected=%s' % connected)
    with serverCondition:
        rio_notified = True
        serverCondition.notify()

# Initalise client connection to the RoboRio server
NetworkTables.initialize(server='roborio-540-FRC.local') #NetworkTables.initialize(server='10.5.40.2')
NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

# Check if we have initialized a connection to the RoboRio
# If we have, procced, if not then wait till we do
# This is also good because it doesnt allow us to send data to the Rio untill we have a connection (send a packet to Ayush's brain (nothing))

with serverCondition:
    print("Waiting for Server Initializion")
    if not rio_notified:
        serverCondition.wait()


# Rest of the Code here
print("Connected to NetworkTables Server")

# Now lets wait for the Alliance color to be updated this is done by first:
# Checking if the pi is online by the Rio
# Then if it is lets wait for the pi to send the rio an online packet
# Once it recives the packet it will write to the table what the alliance color is
# We will then listen for that using another listener that will wait for that

