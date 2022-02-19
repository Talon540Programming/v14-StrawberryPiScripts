# TE.AM ip: 10.5.40.2
# RoboRio Local ip: roboRIO-540-FRC.local

# 1. Connect to RoboRio network
# 2. Run 'ping roboRIO-540-FRC.local' in terminal
# 3. If it is successful then run this script, else troubleshoot

from networktables import NetworkTables

# Initalise client connection to the RoboRio server
NetworkTables.initialize(server='roborio-540-FRC.local')

piTable = NetworkTables.getDefault().getTable("TalonPi")

print(piTable.getEntry("alliance").getString("null"))