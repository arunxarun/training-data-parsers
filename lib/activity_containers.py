'''
Created on Mar 2, 2013

@author: jacoba100
basic point in time (absolute), space (alt/lat/long), and effort (hr)
'''
import math
import json
import logging
from pace import PaceMetric
from pace import metersToFeet
from pace import FEET_IN_METERS
from pace import FEET_IN_MILES
    
#def minutesPerMileFromFeetPerSecond(numFeet,timeSecs):
#    
#    # how many feet in a minute? 
#    feetInMinute = numFeet* (60.0/timeSecs)
#    # how many minutes to complete a mile?
#    minutesToMile = float(FEET_IN_MILES)/feetInMinute
#    
#    return minutesToMile
    
class ActivityContainerEncoder(json.JSONEncoder):

    def default(self, obj):
        if hasattr(obj,'toJSON'):
            return obj.toJSON()
        else:
            return json.JSONEncoder.default(self, obj)

class TrackPoint(object):
    '''
    a TrackPoint is a single point of measurement. Dimensions include:
    lat and long geo coordinates
    altitude -- input in meters
    distance -- input in meters
    current heart rate -- as beats per minute
    '''
    def __init__(self,timeSeconds,latDegrees,lngDegrees,altMeters,distMeters,hrBpm,logger = logging.getLogger("TrackPoint")):
        self.logger = logger
        self.timeSeconds = timeSeconds
        self.latDegrees = latDegrees
        self.lngDegrees = lngDegrees
        
        self.altMeters = altMeters
        self.distMeters = distMeters
        self.hrBpm = hrBpm
        logger.info("date = "+self.timeSeconds.ctime() +" | lat = %f | long = %f | alt = %f | dist = %f | hr = %d"%(self.latDegrees,self.lngDegrees,self.altMeters,self.distMeters,self.hrBpm))
    
    def toJSON(self):
        
        return dict(timestamp = self.timeSeconds.strftime("%Y-%m-%dT%H:%M:%SZ"),latDegrees = self.latDegrees,
                lngDegrees = self.lngDegrees, altMeters=self.altMeters,distMeters = self.distMeters,hrBPM = self.hrBpm)
            
    
class Track(object):
    
    '''
    a Track is a grouping of TrackPoints. Used to provide some level of rollup between single TrackPoint measurements and user defined laps. 
    '''
    def __init__(self,activityType,trackPoints, isMetric = True, logger = logging.getLogger("Track")):
        self.activityType = activityType
        self.logger = logger
        self.trackPoints = []
        self.trackPoints = trackPoints
        self.totalDistMeters = self.getTotalDistMeters()
        self.totalTimeSeconds = self.getTotalTimeSeconds()
        self.altGainedMeters = self.getAltGainedMeters()
        self.altLostMeters = self.getAltLostMeters()
        self.avgHr = self.getAverageHr()
        self.avgPace = self.getAveragePace(False,self.getTotalDistMeters(),self.getTotalTimeSeconds()), # store this in metric
        self.isMetric = isMetric
       
    def toJSON(self):
        return dict(type = self.activityType, 
                    totalDist = self.getTotalDist(self.isMetric,self.totalDistMeters), 
                    totalTimeSeconds = self.totalTimeSeconds, 
                    altGainedMeters = self.getAltGained(self.isMetric,self.altGainedMeters), 
                    altLost = self.getAltLost(self.isMetric,self.altLostMeters), 
                    avgHr = self.avgHr,
                    avgPace = self.getAveragePace(self.isMetric,self.getTotalDistMeters(),self.getTotalTimeSeconds()),
                    trackPoints = self.trackPoints
                    )
             
    '''
    conversion functions, keyed by isMetric
    '''
        
    def getTotalDist(self,isMetric,totalDistMeters):
        if isMetric == True:
            return totalDistMeters
        else:
            return metersToFeet(totalDistMeters)
        
    
    def getAltGained(self,isMetric,altGainedMeters):
        if isMetric == True:
            return altGainedMeters
        else:
            return metersToFeet(altGainedMeters)
            
    def getAltLost(self,isMetric,altLostMeters):
        if isMetric == True:
            return altLostMeters
        else:
            return metersToFeet(altLostMeters)
        
    '''
    basic calc functions, all in meters
    '''
        
    def getAvgTimeStampSeconds(self):
        return self.tps[len(self.tps)/2]
        
    def getAltGainedMeters(self):
        return self.getTotalAltMeters(True)
    
    def getAltLostMeters(self):
        return self.getTotalAltMeters(False)
        
        
    def getTotalAltMeters(self,isGain):
        lastAlt = -1
        curAlt = 0
        altDelta = 0
        
        for tp in self.trackPoints:
            
            
            if lastAlt == -1:
                curAlt = tp.altMeters
                lastAlt = curAlt
            else:
                lastAlt = curAlt
                curAlt = tp.altMeters
            
            
            delta = curAlt - lastAlt
            
            if (delta > 0 and isGain == True) or (delta <=0 and isGain == False):
                altDelta = altDelta + delta
                 
        
        return altDelta
    
    def getAverageHr(self):
        
        totalHr = 0.0
        
        for tp in self.trackPoints:
            totalHr = totalHr + tp.hrBpm
            
        return totalHr/len(self.trackPoints) 
    
    
    def getTotalDistMeters(self):
        return self.trackPoints[len(self.trackPoints)-1].distMeters - self.trackPoints[0].distMeters
    
    def getTotalTimeSeconds(self):
        startTime = self.trackPoints[0].timeSeconds
        endTime  = self.trackPoints[len(self.trackPoints)-1].timeSeconds
        
        diff= endTime - startTime
        return diff.seconds
        
    def getAveragePace(self,isMetric, totalTimeSeconds,totalDistMeters):
        
        avgPace = PaceMetric(self.activityType,isMetric, totalTimeSeconds,totalDistMeters)
                
        return avgPace    
    
class Lap(object):
    
    '''
    a Lap is a track container. It contains the aggregates that exist within user defined laps  
    '''
    def __init__(self, totalTimeSecs,distanceMeters,calories,averageHr,isResting,tracks, isMetric = True,logger = logging.getLogger("Lap")):
        self.totalTimeSecs = totalTimeSecs
        self.distanceMeters = distanceMeters
        self.calories = calories
        self.averageHr = averageHr
        self.altGainedMeters = 0
        self.altLostMeters = 0
        self.isResting = isResting
        self.tracks = []
        
        self.tracks = tracks
        for track in self.tracks:
            self.altGainedMeters += track.getAltGainedMeters()
            self.altLostMeters += track.getAltLostMeters()
    
    def toJSON(self):
        return dict(totalTimeSecs=self.totalTimeSecs,distanceMeters = self.distanceMeters,altGainedMeters = self.altGainedMeters,
                    altLostMeters = self.altLostMeters,calories=self.calories,
                    avgHr = self.averageHr,isResting = self.isResting,tracks = self.tracks)
            
    
   
class Activity(object):
    
    
    def toJSON(self):
        return dict(totalTime=self.totalTime,totalDist=self.totalDist, avgHr = self.getAverageHr(), avgPace=self.getAvgPace(),totalAltGained = self.getAltGained(),
                    totalAltLost = self.getAltLost(),calories = self.totalCalories, laps = self.laps, aggregatedTrackPoints = self.aggregatedTrackPoints)
        
    def __init__(self,act_id,act_type,laps,isMetric = True,logger = logging.getLogger("Activity")):
        self.id = act_id
        self.type = act_type
        self.laps = []
        self.aggregatedTrackPoints = []
        self.totalTimeSecs = 0
        self.totalDistMeters = 0
        self.totalHr = 0
        self.totalAltGainedMeters = 0
        self.totalAltLostMeters = 0
        self.totalCalories = 0
        self.isMetric = isMetric
        
        self.laps = laps
        
        for lap in laps:
            self.totalTimeSecs += lap.totalTimeSecs
            self.totalDistMeters += lap.distanceMeters
            self.totalHr += lap.averageHr
            self.totalCalories += lap.calories
            self.totalAltGainedMeters += lap.altGainedMeters
            self.totalAltLostMeters += lap.altLostMeters
        
        self.avgPace = PaceMetric(self.type,self.isMetric,self.totalTimeSecs,self.totalDistMeters)
        
      
    def getAverageHr(self):
        avgHr = float(self.totalHr)/len(self.laps)
        return avgHr
      
        
    def getAvgPace(self):
        return self.avgPace
    
    def getTimeAsHoursMinutesSeconds(self):
        hours = int(self.totalTimeSecs / 3600)
        minutes = int ((self.totalTimeSecs % 3600)/60)
        seconds = int((self.totalTimeSecs % 3600)%60)
        return hours,minutes,seconds
    
    
    def getFormattedTime(self):
        h,m,s = self.getTimeAsHoursMinutesSeconds()
        
        return "%d:%d:%d"%(h,m,s)
    
    def getDistGranular(self):
        if self.isMetric == True:
            return self.totalDistMeters
        else:
            return self.getDistAsFeet()
        
    def getDistAsFeet(self):
        return self.totalDistMeters*FEET_IN_METERS

    def getDistAggregate(self):
        if self.isMetric:
            return self.totalDistMeters/1000
        else:
            return self.getDistAsMiles()
            
    def getDistAsMiles(self):
        return self.getDistAsFeet()/FEET_IN_MILES
        
    def getAltGained(self):
        if self.isMetric:
            return self.totalAltGainedMeters
        else:
            return self.getAltGainedAsFeet()
        
    def getAltGainedAsFeet(self):
        return self.totalAltGainedMeters*FEET_IN_METERS
    
    def getAltLost(self):
        if self.isMetric:
            return self.totalAltLostMeters
        else:
            return self.getAltLostAsFeet()

    def getAltLostAsFeet(self):
        return self.totalAltLostMeters*FEET_IN_METERS
    
    
        
        
        
    
            
        
        
        
        
            
         
    
    
    
    
        