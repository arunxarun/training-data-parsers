'''
Created on Feb 16, 2013

@author: jacoba100
'''
import sys
import xml.etree.ElementTree as ET
from optparse import OptionParser
import dateutil.parser
import logging
from activity_containers import TrackPoint
from activity_containers import Track
from activity_containers import Lap
from activity_containers import Activity
from activity_containers import ActivityContainerEncoder
import json
import logging

ACTVITIES = '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Activities'
ACTIVITY = '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Activity'
LAP = '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Lap'
TRACK = '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Track'
TIME = '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Time'
POSITION = '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Position'
LAT = '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}LatitudeDegrees'
LONG = '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}LongitudeDegrees'
ALT = '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}AltitudeMeters'
DIST = '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}DistanceMeters'
HRBPM = '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}HeartRateBpm'
HRVAL = '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Value'
TOTALTIME ='{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}TotalTimeSeconds' 
CALORIES = '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Calories'
AVGHR = '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}AverageHeartRateBpm'
INTENSITY = '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Intensity'
VALUE  = '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Value'
ID = '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Id'
'''
{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}DistanceMeters
{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}MaximumSpeed


{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}MaximumHeartRateBpm

{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}TriggerMethod

'''



        
    
class ActivityParser(object):
    '''
    parses actvities into a set of objects
    '''


    def __init__(self,logger,isMetric = False):
        '''
        Constructor
        '''
        self.parsedLaps= []
        self.summary = None
        self.logger = logger
        self.isMetric = isMetric
    
    def parse(self,fileName):
        
        activities = []
        aggregatedTrackPoints = []
        tree = ET.parse(fileName)
        
        
        root = tree.getroot()
        
        activitiesTag = root.find(ACTVITIES)
        
        for activityTag in activitiesTag:
            
            laps = []  
            lapTags = activityTag.findall(LAP)
            act_type  = activityTag.attrib['Sport']
            idTag = activityTag.find(ID)
            act_id = idTag.text
            
            
            
            for lapTag in lapTags:
                tracks = []
                tt = 0
                td = 0
                cc = 0
                hr = 0
                isResting = False
                
                totaltime = lapTag.find(TOTALTIME)
                if(totaltime != None):
                    tt = float(totaltime.text)
                
                totalDistTag = lapTag.find(DIST)
                if(totalDistTag != None):
                    td = float(totalDistTag.text)
                                         
                cals = lapTag.find(CALORIES)
                if(cals != None):
                    cc = float(cals.text)
                
                avgHrTag = lapTag.find(AVGHR)
                if(avgHrTag != None):
                    val = avgHrTag.find(VALUE)
                    avgHr = float(val.text)
                    
                intensity = lapTag.find(INTENSITY)
                if(intensity != None):
                    if(intensity.text == 'Resting'):
                        isResting = True
                    else:
                        isResting = False
                    
                
                
                # TODO: group trackpoints with laps but also group them into buckets of groupBy count. 
                # return these separately. 
                
                trackTags = lapTag.findall(TRACK)
                
                for trackTag in trackTags:
                    
                    trackPoints = []
                    for trackpointTag in trackTag:
                        
                        realtime = ''
                        lat = ''
                        lng = ''
                        alt = ''
                        dist = ''
                        hr = ''
                        
                        ts = 0
                        latDegrees = 0.0
                        lngDegrees = 0.0
                        altMeters = 0.0
                        distMeters = 0.0
                        hrBpm = 0
                        
                        timesec = trackpointTag.find(TIME)
                        if timesec != None:
                            realtime = timesec.text
                            d2 = dateutil.parser.parse(realtime)
                            ts = d2.astimezone(dateutil.tz.tzutc())
                        else:
                            ts = None
                            
                        pos = trackpointTag.find(POSITION)
                        if pos != None:
                            lat = pos.find(LAT)
                            latDegrees = float(lat.text)
                            lng = pos.find(LONG)
                            lngDegrees = float(lng.text)
                        else:
                            latDegrees = lngDegrees = 0
                        
                        alt = trackpointTag.find(ALT)
                        if alt != None:
                            altMeters = float(alt.text)
                        else:
                            alt = 0
                            
                        
                        dist = trackpointTag.find(DIST)
                        if dist != None:
                            distMeters = float(dist.text)
                        else:
                            distMeters = 0
                            
                        hrb = trackpointTag.find(HRBPM)
                        
                        if hrb != None:
                            hr = hrb.find(HRVAL)
                            hrBpm = int(hr.text)
                        else:
                            hrBpm = 0
                        
                        tp = TrackPoint(ts,latDegrees,lngDegrees,altMeters,distMeters,hrBpm)
                        trackPoints.append(tp)
                        
                    track = Track(act_type,trackPoints)
                    tracks.append(track)
                
                # (self, totalTimeSecs,distanceFeet,calories,averageHr,isResting,logger):
                lap = Lap(tt,td,cc,avgHr,isResting,tracks,self.logger)
                laps.append(lap)
       
            activity = Activity(act_id,act_type,laps,self.isMetric)
            activities.append(activity)
            
        return activities
                
if __name__ == "__main__":
    
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                          help="parse FILE", metavar="FILE")
    parser.add_option("-g", "--groupBy", type="int",dest="groupBy")
    (options, args) = parser.parse_args()
        
    filename = options.filename
    
    if filename == None:
        print 'usage: python activityparser.py -f [filename] {-c groupBy (default = 10)}'
        sys.exit()
        
    groupBy = options.groupBy
    
    if groupBy == None:
        groupBy = 10
    logger = logging.getLogger('activityparser')
    hdlr = logging.FileHandler('./testoutput/activityparser.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)   
    
    ap = ActivityParser(logger)
    activities = ap.parse(filename,groupBy)
    
    for activity in activities:
        print json.dumps(activities,cls = ActivityContainerEncoder)
        
    # persist these to Cassandra? 
        