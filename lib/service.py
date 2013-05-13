'''
Created on Mar 28, 2013

@author: jacoba100

test REST service that returns information about exercise data.
'''

from bottle import route, run, template, TEMPLATE_PATH, request
import os
import json
import logging
from datetime import datetime
from datetime import timedelta

from activityparser import ActivityParser

allActivities = {}

def convertToUrlPart(activityId):
    # assume TZ formatting:convert colons to underbars
    newId = activityId.replace(':','_')
    return newId 
    
@route('/exerdata/:month/:day/:year/summary')
def getDataForDay(month,day,year):
   return json.dumps("{'month':month, 'day':day, 'year':year, 'activities':[{'id'='2013-02-12T14:32:00Z','type'= 'running','totalDistMiles' = 2.92, 'totalAltGained'=2250, 'totalAltLost'=2300}]}") 

@route('/exerdata/uploadpage')
def showUpload():
    return template('file_upload')

@route('/exerdata/home')
def home():
    return template('home')

@route('/exerdata/datasummaries')
def datasummaries():
    return template('data_summaries')



@route('/upload', method='POST')
def uploadFile():
    upload     = request.files.get('upload')
    
    name, ext = os.path.splitext(upload.filename)
    if ext not in ('.tcx'):
        return 'File extension not allowed.'

    save_path = '/tmp/'
    data = upload.value # appends upload.filename automatically
    
    fn = save_path+name+ext
    fp = open(fn,'w')
    fp.write(data)
    fp.close()
    
    
    groupBy = 10
    logger = logging.getLogger('activityparser')
    hdlr = logging.FileHandler('./testoutput/activityparser.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)   
    
    ap = ActivityParser(logger)
    parsedActivities = ap.parse(fn,groupBy)
    
    for activity in parsedActivities:
        allActivities[convertToUrlPart(activity.id)] = activity
           
    return template('data_summaries',activities=parsedActivities)
    

@route('/sampleviz/listdata')
def listdata():
    
    graph = {'title' : 'Elevation Gain/Loss','type': 'line'}
    
    datasequences = []
    datasequence = {'title':'run1'}
    datapoints = []
    goingUp = True
    elevation = 100
    
    timestamp = datetime.now()
    second = timedelta(seconds = 1)
    
    for i in range(1,1000) :
        if i % 100 == 0:
            goingUp = not goingUp
        
        if goingUp == True:
            elevation +=1
        else:
            elevation -=1
        timestamp = timestamp + second
        titleString = timestamp.strftime('%H:%M:%S')
        elevationString = '%d'%elevation
        datapoints.append({'title': titleString,'value' : elevationString})
        
    datasequence['datapoints'] = datapoints
    datasequences.append(datasequence)
    graph['datasequences'] = datasequences
    wrapper = {}
    wrapper['graph'] = graph
    
    data = json.dumps(wrapper)

    

    return data

if __name__ == '__main__':
    run(host='localhost', port=8080)


