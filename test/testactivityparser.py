'''
Created on Feb 28, 2013

@author: jacoba100
'''
import unittest
import time
import dateutil.parser
import logging
from activityparser import ActivityParser
class Test(unittest.TestCase):


    def testTimeStingParse(self):
        ' test time conversion for parsing.'
        timestr = '2013-02-12T15:16:53Z'
        
        
        timestruct = time.strptime(timestr,"%Y-%m-%dT%H:%M:%SZ")
        
        
        d2 = dateutil.parser.parse(timestr)
        d3 = d2.astimezone(dateutil.tz.tzutc())

        val = d3.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        Test.assertEqual(self,val,timestr)
        
        
    def testActivityParse(self):
        'test basic parsing'
        
        fname = './resources/testdata.tcx'
        groupBy = 10
        logger = logging.getLogger('activityparser')
        hdlr = logging.FileHandler('./testoutput/activityparser.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
        logger.setLevel(logging.INFO)   
        
        ap = ActivityParser(logger)
        activities = ap.parse(fname)
        
        self.assertEqual(1,len(activities))
        laps = activities[0].laps
        aggregatedTrackPoints = activities[0].aggregatedTrackPoints
        self.assertFalse(laps == None)
        self.assertFalse(aggregatedTrackPoints == None)
        
        self.assertEquals(1,len(laps))
        self.assertEquals(1,len(laps[0].tracks))
        self.assertEquals(1,len(laps[0].tracks[0].trackPoints))
        lap = laps[0]
        
        # NOT testing container functionality, just testing parsing. 
        
        self.assertAlmostEquals(lap.distanceMeters,4203.955,3)
        self.assertAlmostEquals(lap.totalTimeSecs,1526.6,1)
        self.assertEquals(lap.calories,557)
        self.assertEquals(lap.averageHr,134)
        self.assertEquals(lap.isResting,True)
        
        
        
    
    def testBulkActivityParse(self):
        ' test that a bulk (multiday) download works'
        'whoops, this breaks our shit. We want to roll laps and aggregates up into summary activities.'
        doneYet = False
        self.assertEquals(True,doneYet)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testTimeStingParse']
    unittest.main()