FEET_IN_METERS = 3.28084
FEET_IN_MILES = 5280
SECONDS_IN_HOUR = 3600
def metersToFeet(self,numMeters):
    return numMeters*FEET_IN_METERS
    
def feetToMiles(self,numFeet):
    return float(numFeet)/FEET_IN_MILES



class Pace(object):
    def __init__(self,isMetric):
        self.isMetric = isMetric
        
    
    def toJSON(self):
        return dict(isMetric = self.isMetric, 
                    pace=self.getPace())
        
    def toString(self):
        return "%f"%self.getPace()
 
class PaceMetric(Pace):
    def __init__(self,activityType,isMetric,totalTimeSecs,totalDistMeters):
        Pace.__init__(self,isMetric)
        self.activityType = activityType
        self.totalDistMeters = totalDistMeters
        self.totalTimeSecs = totalTimeSecs
        self.unitsOfMeasurement = None
        
    def toString(self):
        return "%f %s"%(self.getPace(),self.unitsOfMeasurement)
    
    def getPace(self):
        if self.activityType == "Running":
            if self.isMetric == True:
                return self.minutesPerKilometer()
            else: 
                return self.minutesPerMile()
        elif self.activityType == "Cycling":
            if self.isMetric == True:
                return self.kilometersPerHour()
            else:
                return self.milesPerHour()
            
    def minutesPerKilometer(self):
        self.unitsOfMeasurement = "minutes/km"
        minutes = float(self.totalTimeSecs)/60
        kilometers = float(self.totalDistMeters)/1000
        pace = minutes/kilometers 
        return pace
  
    def minutesPerMile(self):
        self.unitsOfMeasurement = "minutes/mile"
        totalDistFeet = self.totalDistMeters*FEET_IN_METERS
        totalDistMiles = totalDistFeet/FEET_IN_MILES
        totalTimeMinutes = self.totalTimeSecs/60
        
        pace = totalTimeMinutes/totalDistMiles
        return pace
        
    def kilometersPerHour(self):
        pace = float(self.totalDistMeters)/self.totalTimeSecs # now meters per second
        pace = pace/1000 # now kilometers per second
        pace = pace*SECONDS_IN_HOUR # now kilometers per hour
        
        
    def milesPerHour(self): 
        totalDistMiles =  ((self.totalDistMeters)*FEET_IN_METERS)/FEET_IN_MILES
        totalTimeHours = self.totalTimeSecs/SECONDS_IN_HOUR
        pace = float(totalDistMiles)/totalTimeHours # now meters per second
        
    