'''
Created on Mar 2, 2013

@author: jacoba100
'''
import unittest
import logging
from activity_containers import TrackPoint
from activity_containers import Track
from activity_containers import ActivityContainerEncoder
from activity_containers import Lap
import datetime
import json
from time import sleep
class Test(unittest.TestCase):


    def testTrackPointsGetTotalAlt(self):
        logger = logging.getLogger('testlogger')
        tps = []
        latDeg = 40.0
        lngDeg = 40.0
        altMeters = 300
        distMeters = 0
        hrBpm = 120
        
        for i in range(0,5):
            dt = datetime.datetime.now()
            
            tp = TrackPoint(dt,latDeg,lngDeg,altMeters,distMeters,hrBpm)
            tps.append(tp)
            latDeg = latDeg + 0.1
            lngDeg = lngDeg + 0.1
            altMeters = altMeters + 1
            distMeters = distMeters + 1
            hrBpm = hrBpm + i
            sleep(1)

        
        track = Track('Running',tps)
        self.assertAlmostEquals(track.getAltGainedMeters(), 4, 2)
        
        


    def testGetAverageHr(self):
        logger = logging.getLogger('testlogger')
        tps = []
        latDeg = 40.0
        lngDeg = 40.0
        altMeters = 300
        distMeters = 0
        hrBpm = 120
        totalhr= 0
        for i in range(0,6):
            dt = datetime.datetime.now()
            totalhr = totalhr+hrBpm
            tp = TrackPoint(dt,latDeg,lngDeg,altMeters,distMeters,hrBpm)
            tps.append(tp)
            latDeg = latDeg + 0.1
            lngDeg = lngDeg + 0.1
            altMeters = altMeters + 1
            distMeters = distMeters + 1
            hrBpm = hrBpm + 1
            
        track = Track('Running',tps)    
        avgHr = track.getAverageHr()
        self.assertEquals(122.5,avgHr)
    
    
    
    def testThatWeCanSubtractTime(self):
        
        dt = datetime.datetime.now()
        sleep(1)
        dt2 = datetime.datetime.now()
        
        dtDiff = dt2-dt
        dtTest = datetime.timedelta(seconds=1)
        self.assertAlmostEqual(dtTest.seconds, dtDiff.seconds)
        
    def testGetAveragePace(self):
        
        logger = logging.getLogger('testlogger')
        
        latDeg = 40.0
        lngDeg = 40.0
        altMeters = 300
        distMeters = 0
        hrBpm = 120
        
        tps= []
        for i in range(0,5):
            dt = datetime.datetime.now()
            
            tp = TrackPoint(dt,latDeg,lngDeg,altMeters,distMeters,hrBpm)
            tps.append(tp)
            latDeg = latDeg + 0.1
            lngDeg = lngDeg + 0.1
            altMeters = altMeters + 1
            distMeters = distMeters + 1
            hrBpm = hrBpm + i
            
            sleep(1)
        
        track = Track('Running',tps)
        mpk = track.getAveragePace(track.isMetric,track.totalTimeSeconds,track.totalDistMeters)
        
        self.assertFalse(mpk == None)
        p = mpk.getPace()
        self.assertNotEqual(p, 0,'avg speed should not == 0')
        self.assertAlmostEqual(p, 16.67, 2, 'should be equal to 16.67 Km/Minute')
        
        
    
            
            
    def testGetTotalTime(self):
        
        latDeg = 40.0
        lngDeg = 40.0
        altMeters = 300
        distMeters = 0
        hrBpm = 120
        logger = logging.getLogger('testlogger')
        tps = []
        
        for i in range(0,4):
            dt = datetime.datetime.now()
            tp = TrackPoint(dt,latDeg,lngDeg,altMeters,distMeters,hrBpm)
            tps.append(tp)
            
            latDeg = latDeg + 0.1
            lngDeg = lngDeg + 0.1
            altMeters = altMeters + 1
            distMeters = distMeters + 1
            hrBpm = hrBpm + i
            sleep(1)
        
        track = Track('Running',tps)
        time = track.getTotalTimeSeconds()
        tdelta = datetime.timedelta(seconds = 3)
        self.assertAlmostEqual(tdelta.seconds, time)
        
    def testJSON(self):
        
        logger = logging.getLogger('testlogger')
        tps = []
        latDeg = 40.0
        lngDeg = 40.0
        altMeters = 300
        distMeters = 0
        hrBpm = 120
        
        for i in range(0,5):
            dt = datetime.datetime.now()
            
            tp = TrackPoint(dt,latDeg,lngDeg,altMeters,distMeters,hrBpm)
            tps.append(tp)
            
            latDeg = latDeg + 0.1
            lngDeg = lngDeg + 0.1
            altMeters = altMeters + 1
            distMeters = distMeters + 1
            hrBpm = hrBpm + i
            sleep(1)
            test =  json.dumps(tp,cls=ActivityContainerEncoder)
            jsonObj = json.loads(test)
            self.assertFalse(None == jsonObj)
            self.assertEquals(latDeg-0.1,jsonObj['latDegrees'])
            self.assertEquals(lngDeg-0.1,jsonObj['lngDegrees'])
            
        track = Track('Running',tps)
        test =  json.dumps(track,cls=ActivityContainerEncoder)
        jsonObj = json.loads(test)
        self.assertFalse(None == jsonObj['trackPoints'])
        self.assertFalse(0 == len(jsonObj['trackPoints']))
        self.assertEquals(120,jsonObj['trackPoints'][0]['hrBPM'])
        tracks = []
        tracks.append(track)
        lap = Lap(track.getTotalTimeSeconds(),track.getTotalDistMeters(),10000,track.getAverageHr(),False,tracks)
        
        test = json.dumps(lap,cls=ActivityContainerEncoder)
        jsonObj = json.loads(test)
        self.assertTrue(len( jsonObj['tracks']) == 1)
        self.assertTrue(len(jsonObj['tracks'][0]['trackPoints']) == 5)
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testTrackPointsGetTotalAlt']
    unittest.main()