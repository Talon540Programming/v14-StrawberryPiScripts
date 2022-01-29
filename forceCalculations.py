import math

def shooterCalculations(distanceFromTopHub):
#   hubStackHeight = 109/8 #Feet
#   LimelightSensorHeight = 13/3 #Feet
  
  hubHeight = 2.64 #meters
  limeLightHeight = 1.321 #meters
  shooterHeight = 0 #meters
  distanceFromTopHub = (distanceFromTopHub/3.281) + 0.1 #converts feet to meters and determines the shooters distance from the 
  AoA = math.radians(-20)
  # Get Limelight Data
  # Convert to Feet

  # hubStackHeight = hubStackHeight-LimelightSensorHeight
  
  distanceFromHubBase = math.sqrt(math.pow(distanceFromTopHub,2)-math.pow((hubHeight-limeLightHeight),2))
  rawShooterAngle = math.asin((hubHeight-limeLightHeight)/(distanceFromTopHub))
  
  shootingAngle = math.degrees(math.atan(((distanceFromHubBase * math.tan(AoA)) - (2 * (hubHeight-limeLightHeight)))/(-distanceFromHubBase)))
  shootingSpeed = 0 

  # Add physics and calculus here. Update angle. Get speed

  print("Shooter Angle: "+str(shootingAngle))
  print("Distance from Hubs: "+str(distanceFromHubBase))
  
  return (rawShooterAngle, distanceFromHubBase)

dist = input("Enter Distance: ")
shooterCalculations(20) #Leave this for now
