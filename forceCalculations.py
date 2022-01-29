# -*- coding: utf-8 -*-
import math

def shooterCalculations(distanceFromTopHub):
#   hubStackHeight = 109/8 #Feet
#   LimelightSensorHeight = 13/3 #Feet
  
  hubHeight = 2.64 #meters
  limeLightHeight = 1.321 #meters
  shooterHeight = 0.5 #meters
  distanceFromTopHub = (distanceFromTopHub/3.281) #converts feet to meters
  AoA = math.radians(-20) # Angle at which the ball goes into the hub
  # Get Limelight Data
  
  H = hubHeight-shooterHeight # Height difference of hub and shooter
  # hubStackHeight = hubStackHeight-LimelightSensorHeight
  
  d = math.sqrt(math.pow(distanceFromTopHub,2)-math.pow((hubHeight-limeLightHeight),2)) + 0.2 # Distance from hub base to shooter
  # rawShooterAngle = math.asin((hubHeight-limeLightHeight)/(distanceFromTopHub))
  
  shootingAngle = math.degrees(math.atan(((d * math.tan(AoA)) - (2 * (H)))/(-d)))
  shootingSpeed = math.sqrt(-((9.81 * math.pow(d, 2) * (1 + (math.pow((math.tan(math.radians(shootingAngle))), 2)))/((2 * H)-(2 * d * math.tan(math.radians(shootingAngle)))))))

  print("Shooting Speed: " + str(shootingSpeed))
  print("Shooter Angle: "+str(shootingAngle))
  print("Distance from Hubs: "+str(d))
  
  return (shootingSpeed, shootingAngle)

dist = float(input("Enter Distance: ")) # Needs to Recieve distance to hub top from Limelight
speed, angle = shooterCalculations(dist) #speed in in m/s and angle is in degrees

# send speed and angle elsewhere
