import math

def shooterCalculations(distanceFromTopHub):
  hubStackHeight = 109/8 #Feet
  LimelightSensorHeight = 13/3 #Feet

  # Get Limelight Data
  # Convert to Feet

  hubStackHeight = hubStackHeight-LimelightSensorHeight
  distanceFromHubBase = math.sqrt(math.pow(distanceFromTopHub,2)-math.pow(hubStackHeight,2))
  rawShooterAngle = math.asin((hubStackHeight)/(distanceFromTopHub))

  # Add physics and calculus here. Update angle. Get speed

  print("Shooter Angle: "+str(rawShooterAngle))
  print("Distance from Hubs: "+str(distanceFromHubBase))
  
  return (rawShooterAngle, distanceFromHubBase)

dist = input("Enter Distance: ")
shooterCalculations(20) #Leave this for now
