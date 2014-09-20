'''
Created on Sep 19, 2014

@author: kwalker
'''
class SegmentResult(object):
    """Stores the results of a single geocode. Also contains static methods for writing a list
    AddressResults to different formats."""
  
    def __init__(self, segmentId, signal, uplink, downlink,):
        self._segmentId = segmentId
        self._signal = signal
        self._uplink = uplink
        self._downlink = downlink
    
    def __str__(self):
        return "{},{},{},{}".format(self._segmentId, self._signal, self._uplink, 
                                       self._downlink)
    
#     @staticmethod
#     def addHeaderResultCSV(outputFilePath):
#         with open(outputFilePath, "a") as outCSV:
#             outCSV.write("{},{},{},{},{},{},{},{},{}".format("OBJID", "INADDR", "INZONE", 
#                                                       "MatchAddress", "Zone", "Score", 
#                                                       "XCoord", "YCoord", "Geocoder" ))
    @staticmethod
    def appendResultCSV(segResult, outputFilePath): 
        with open(outputFilePath, "a") as outCSV:
            outCSV.write("\n" + str(segResult))

    
    @staticmethod
    def createResultCSV(segResultList, outputFilePath):
        """Replaced by appending method"""
        with open(outputFilePath, "w") as outCSV:
            outCSV.write("{},{},{},{}".format("segmentID", "signal", "uplink", 
                                                          "downlink"))
            for result in segResultList:
                outCSV.write("\n" + str(result))
                
                
if __name__ == "__main__":
    
    