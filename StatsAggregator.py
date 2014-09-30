'''
Created on Sep 19, 2014

@author: kwalker
'''
import arcpy, os, csv

class Fields (object):
    
    def __init__(self):
        self._fieldList = []
        
    def getI(self, field):
        return self._fieldList.index(field)
    
    def getFieldList(self):
        return self._fieldList


class DataPointFields(Fields):
    
    def __init__(self, dataPoints, directionFieldName, speedFieldName):        
        self.objectId = arcpy.Describe(dataPoints).OIDFieldName
        self.direction = directionFieldName
        self.speed = speedFieldName
        
        self._fieldList = [self.objectId, self.direction, self.speed]
        
class signalPointFields(Fields):
    
    def __init__(self, signalPoints, signalFieldName):        
        self.objectId = arcpy.Describe(signalPoints).OIDFieldName
        self.signal = signalFieldName
        
        self._fieldList = [self.objectId, self.signal]

class NearTableFields(Fields):

    def __init__(self):
        self.inputId = 'IN_FID'
        self.nearId = 'NEAR_FID'
        
        self._fieldList = [self.inputId, self.nearId]

class DataStatsFields(Fields):
    
    def __init__(self, dataFields, nearFields):
        self.segmentId = nearFields.nearId 
        self.maxSpeed = 'MAX_{}'.format(dataFields.speed)
        self.direction = dataFields.direction
        
        self._fieldList = [self.segmentId, self.maxSpeed, self.direction]

class SignalStatsFields(Fields):
    
    def __init__(self, signalFields, nearFields):
        self.segmentId = nearFields.nearId 
        self.maxSignal= 'MAX_{}'.format(signalFields.signal)
        
        self._fieldList = [self.segmentId, self.maxSignal]       
        
class SegmentResult(object):
    """Stores the results of a single segment. Also contains static methods for writing a list
    SegmentResults to CSV format."""
    
    outputCsvFields = []
  
    def __init__(self, segmentId):
        self._segmentId = segmentId
        self.signal = ""
        self.uplink = ""
        self.downlink = ""
        
        if SegmentResult.outputCsvFields == []:#Just in case outputCsvFields doesn't get set, use class fields instead
            SegmentResult.outputCsvFields = self.__dict__.keys()

    
    def getRowList (self):
        return [self._segmentId, self.signal, self.uplink, self.downlink]    
    
    def __str__(self):
        return str(self._rowList)
    
    @staticmethod
    def appendResultCSV(segResult, outputFilePath): 
        with open(outputFilePath, "a") as outCSV:
            outCSV.write("\n" + str(segResult))

    
    @staticmethod
    def createResultCSV(segResultList, outputFilePath):
        """Replaced by appending method"""
        with open(outputFilePath, "wb") as outCSV:
            writer = csv.writer(outCSV)
            writer.writerow(SegmentResult.outputCsvFields)
            writer.writerows(list(segRes.getRowList() for segRes in segResultList))

                
                
if __name__ == '__main__':
     
### Set variables in this section

    #Path to gdb that contains points and segment lines
    gdbPath = r'C:\Users\kwalker\Documents\Aptana Studio 3 Workspace\BroadbandDriveTestStats\data\TestData.gdb'
    #Segment line layer
    roads = '{}'.format(os.path.join(gdbPath, 'MultipleRoadSegments'))#Change the segmentlayer name here    
    #Point layer names and field names
    dataPoints = '{}'.format(os.path.join(gdbPath,'DataPointFeatures'))#Change the data point layer name here
    dataFields = DataPointFields (dataPoints, 'direction', 'speed')#Change direction and speed field names here
    signalPoints = '{}'.format(os.path.join(gdbPath,'SignalPointFeatures'))#Change the signal point layer name here
    signalFields = signalPointFields (signalPoints, 'signal')#Change signal field name here
    #Ouput Csv file path. This csv will be created by the program.
    outputCsvPath =r'C:\Users\kwalker\Documents\Aptana Studio 3 Workspace\BroadbandDriveTestStats\data\OutTest2.csv'
    SegmentResult.outputCsvFields = ["segmentID", "signal", "uplink", "downlink"]#Number of CSV fields should match class fields in SegmentResult
    #Distance that determines is points belong to a segment
    bufferRadius = '0.11 Miles'#Unit text is required by GenerateNearTable_analysis
    
### End set section
    
    tempGdb = 'in_memory'
    dataNearTable = '{}'.format(os.path.join(tempGdb,'DataNear'))
    nearFields = NearTableFields()
    dataStats = '{}'.format(os.path.join(tempGdb, 'dataStats'))
    dStatsFields = DataStatsFields(dataFields, nearFields)
    
    signalNearTable = '{}'.format(os.path.join(tempGdb,'SignalNear'))
    nearFields = NearTableFields()
    signalStats = '{}'.format(os.path.join(tempGdb, 'signalStats'))
    sStatsFields = SignalStatsFields(signalFields, nearFields)
    
    results = {}
    
     
### Data Points
    print "Begin data points near and stats analysis"
    arcpy.GenerateNearTable_analysis (dataPoints, roads, dataNearTable, 
                                      search_radius = bufferRadius, closest = 'ALL', method = 'GEODESIC')
    arcpy.JoinField_management (dataNearTable, nearFields.inputId, dataPoints, 
                                dataFields.objectId, [dataFields.speed, dataFields.direction])
    arcpy.Statistics_analysis (dataNearTable, dataStats, 
                               [[dataFields.speed, 'MAX']], [dataFields.direction, nearFields.nearId])
    
    #Create result objects from stats table
    with arcpy.da.SearchCursor(dataStats, dStatsFields.getFieldList()) as dataCursor:
        for row in dataCursor:            
            segmentId = int(row[dStatsFields.getI(dStatsFields.segmentId)])
            direction = str(row[dStatsFields.getI(dStatsFields.direction)])
            maxSpeed = str(row[dStatsFields.getI(dStatsFields.maxSpeed)])
            
            if segmentId not in results:
                results[segmentId] = SegmentResult(segmentId)
                 
            segResult = results[segmentId]
            
            if direction == 'D':    
                segResult.downlink = maxSpeed
            elif direction == 'U':
                segResult.uplink = maxSpeed
                
    
### Signal points
    print "Begin signal points near and stats analysis"
    arcpy.GenerateNearTable_analysis (signalPoints, roads, signalNearTable, 
                                      search_radius = bufferRadius, closest = 'ALL', method = 'GEODESIC')
    arcpy.JoinField_management (signalNearTable, nearFields.inputId, signalPoints, 
                                signalFields.objectId, [signalFields.signal])
    arcpy.Statistics_analysis (signalNearTable, signalStats, 
                               [[signalFields.signal, 'MAX']], [nearFields.nearId])
    
    #Create result objects from stats table
    with arcpy.da.SearchCursor(signalStats, sStatsFields.getFieldList()) as signalCursor:
        for row in signalCursor:            
            segmentId = int(row[sStatsFields.getI(sStatsFields.segmentId)])
            maxSignal = str(row[sStatsFields.getI(sStatsFields.maxSignal)])
            
            if segmentId not in results:
                results[segmentId] = SegmentResult(segmentId)
                 
            segResult = results[segmentId]
            segResult.signal = maxSignal

### Write results to a CSV file
    SegmentResult.createResultCSV(results.values(), outputCsvPath) 
    arcpy.Delete_management(tempGdb)