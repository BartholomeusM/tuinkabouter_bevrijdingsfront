import fmeobjects
import xml.etree.ElementTree as ET
import os,fnmatch


#------------------------------------------------------------------------------------------------------------
#
#	Python code writen by A. Dames, Atos Nederland BV (andre.dames@atos.net), jun 2014
#
#------------------------------------------------------------------------------------------------------------		
#                                               DESCRIPTION                      
#
# This file will be used in the GEOBASEII validation and mapping process. This file will read the INCONTROL 
# delivery location and then use INCONTROL rules file together with the GIS rules file to supply the FME
# workbenches with parameters within an FME workspace PyCaller transformer
#
#------------------------------------------------------------------------------------------------------------
#												PYTHON CLASSES
#
#	Initialiser():       		Class to perform initial set-up tasks
#   switch():            		Utility class to implement the C# switch structure
#   FeatureProcessor(object)	FME PyCaller interface
#------------------------------------------------------------------------------------------------------------
#                                               PYTHON FUNCTIONS
#
#   LocateFiles:        Scan a specific directory for the INCONTROL rules and text files.
#   ExtractTVSData:     Inspects the INCONTROL rule file and returns the TVS and it's version
#   CollectXPathValues: Returns an array with values from given XPath
#   case:               Needed by the switch class
#
#
#
#------------------------------------------------------------------------------------------------------------
#                                               HISTORY
# 12-June-2014: Initial Creation        							A. Dames
# 23-June-2014: Adapted for PythonCaller transformer in FME			B. Monné
#
#------------------------------------------------------------------------------------------------------------


# Declarations

gisRulesFile = 'C:\\Users\\a503449\\Documents\\Projecten\\ProRail\\GeobaseTVS7\\PoC\Input\\GeobaseGis_Rules_TVS00002_V04.xml'
searchDir = 'C:\\Users\\a503449\\Documents\\Projecten\\ProRail\\GeobaseTVS7\\PoC\\Input'

# Scan recursive through sourceDir for XML files 
def LocateFiles(sourceDir):
    resultList = list()
    try:
        if os.path.exists(sourceDir):
            for file in fnmatch.filter(os.listdir(searchDir),"*.xml"):
                resultList.append(file)
        else:
            raise
    except:
        resultList = None
    finally:
        return resultList

#extract the TVS and it's version from the received xml file
def ExtractTVSData(ruleFileName):
    data = {}
    try:
        data["version"] = ruleFileName[str.rfind(ruleFileName,"-") + 2:str.rfind(ruleFileName,".")]
        data["type"] = ruleFileName[str.rfind(ruleFileName,"_") + 1:str.rfind(ruleFileName,"-")]
    except:
        raise Exception
    finally:
        return data

#fetches the values from the xpath string
def CollectXPathValues(xpathValue,tvsType):
    results = {}
    doc = ET.parse(gisRulesFile)
    for parent in doc.findall(str(xpathValue).replace('%TVSPLACEHOLDER%',tvsType)):
        if parent.text != '\n      ' and parent.text != None:
            parentValue = parent.text
            results["values"] = parentValue.split(",")
        else:
            attribValue = parent.get("values") 
            if attribValue != None:
                results["values"] = attribValue.split()
            else:
                for child in parent:
                    if child.get("name") != None:
                        results[child.get("name")] = child.text
                    else:
                        results[child.text] = child.text                

    return results
  
def case(*args):
    return any((arg == switch.value for arg in args))


class Initialiser():

    def __init__(self, gisrulesFile, sourceDir ):
        self.tvsData = {}
        self._ruleFile = gisrulesFile
        self._dropLocation = sourceDir
        self.ErrorMessage = ""
        self.StateIsOk = bool(1!=1)
        self.DgnFilesOk = bool(1!=1)

    def GetRules(self):
        incontrolFiles = LocateFiles(self._dropLocation)
        try:
            if incontrolFiles != None:
                for item in incontrolFiles: 
                    if str.find(item,"_errors") != -1: #We look for the INCONTROL error file
                        #Now we open this file to see if the INCONTROL process was successful
                        errorDoc = ET.parse(self._dropLocation + "\\{0}".format(item))
                        errorRootNode = errorDoc.getroot()
                        errorChildNodes = errorRootNode.getchildren()            
                        if errorChildNodes: #Process was not ok
                            raise Exception("The error controlfile {0} contains errors! Process wil terminate.".format(item))
                    else: #We process the rule file NB! We assume that we only have two xml files in directory
                       self.tvsData = ExtractTVSData(item)
                if self.tvsData:
                    rulesCollection = {}
                    gisRuleDoc = ET.parse(self._ruleFile)
                    for node in gisRuleDoc.findall(".//rules/validations/rule[@version='{0}']".format(self.tvsData["version"])):                           
                        ruleValues = {} #Collection of all the rules
                        ruleValues["what"] = node.get("what")                
                        if node.get("levels") == "*":
                            ruleValues["levels"] = node.get("levels")
                        else:
                            ruleValues["levels"] = CollectXPathValues(node.get("levels"),self.tvsData["type"])
                        ruleValues["transformerTypes"] = node.get("transformerTypes")
                        ruleValues["errorCode"] = node.get("errorCode")
                        ruleValues["errorMessage"] = node.text                
                        if  node.get("conditionIsXpath") == "true":                
                            ruleValues["condition"] = CollectXPathValues(node.get("condition"),self.tvsData["type"])
                        else:
                            ruleValues["condition"] = node.get("condition")
                        rulesCollection[node.get("name")] = ruleValues
                        self.StateIsOk = bool(1==1)
        except Exception as exc:
            self.ErrorMessage = "The following message was received from verification process \n {0}".format(exc.args[0])
            rulesCollection = None
        finally:            
            return rulesCollection

    def GetDrawingFileNames(self):
        fileList = []
        try:
           for dirpath, dirnames, filenames in os.walk(self._dropLocation):
               for entry in filenames:
                   if str(entry).endswith(".dgn"):
                       fullFileName = os.path.join(dirpath,entry)
                       #Only add if it's a file and not already added
                       if os.path.isfile(fullFileName) and fileList.count(fullFileName) <= 0:
                            fileList.append(fullFileName)
        except:
            fileList = None
        finally:
            self.DgnFilesOk = bool(1==1)
            fileList.sort()
            return fileList

    def close(self):
        pass

class switch(object):
    value = None
    def __new__(class_, value):
        class_.value = value
        return True


# FME Python Caller Interface:
class FeatureProcessor(object):
    def __init__(self):
        pass
    def input(self,feature):
        
        try:
            
            # logging prints
            
            print("validationCounter: " + str(feature.getAttribute("_validationCounter")))
            print("Verwerken van feature " + str(feature.getAttribute("igds_graphic_group")))
            
            
            
            starter = Initialiser(gisRulesFile,searchDir)
     
            validationRules = starter.GetRules()
            
            
            
            # ToDo Name to be determined from list of validations
            
            validationName = "objectInsideCountry"
            
            
            currentValidationParameters = validationRules[validationName]
            
            # print(currentValidationParameters)
            
            # set feauture attributes from current validation
            
            feature.setAttribute("_validationName", validationName) 
            feature.setAttribute("_validationWhat", str(currentValidationParameters["what"]))
            feature.setAttribute("_validationCondition", str(currentValidationParameters["condition"]))
            feature.setAttribute("_validationLevels", str(currentValidationParameters["levels"]))
            feature.setAttribute("_validationErrorcode", str(currentValidationParameters["errorCode"]))
            feature.setAttribute("_validationTransformerType", str(currentValidationParameters["transformerTypes"])) #todo : 's' te veel?
        except Exception, err:
            print('ERROR: %s\n' % str(err))
        finally:
            self.pyoutput(feature)
        
    def close(self):
        pass


