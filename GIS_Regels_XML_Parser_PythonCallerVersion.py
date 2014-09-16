import xml.etree.ElementTree as ET
import os, fnmatch


# ------------------------------------------------------------------------------------------------------------
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
#   extract_tvs_version:     Inspects the INCONTROL rule file and returns the TVS and it's version
#   CollectXPathValues: Returns an array with values from given XPath
#   case:               Needed by the switch class
#
#
#
#------------------------------------------------------------------------------------------------------------
#                                               HISTORY
# 12-June-2014: Initial Creation        							A. Dames
# 23-June-2014: Adapted for PythonCaller transformer in FME			B. Monne
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
            for file in fnmatch.filter(os.listdir(sourceDir), "*.xml"):
                resultList.append(sourceDir + file)
        else:
            raise
    except:
        resultList = None
    finally:
        return resultList


#fetches the values from the xpath string
def CollectXPathValues(gis_rules_file, xpathValue, tvsType):
    results = {}
    doc = ET.parse(gis_rules_file)
    for parent in doc.findall(str(xpathValue).replace('%TVSPLACEHOLDER%', tvsType)):
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
    def __init__(self, gisrulesFile, sourceDir, incontrol_errors_xml, incontrol_rules_xml):

        self.tvs_data = {}
        self._ruleFile = gisrulesFile
        self._dropLocation = sourceDir
        self.incontrol_errors_xml = incontrol_errors_xml
        self.incontrol_rules_xml = incontrol_rules_xml
        self.ErrorMessage = ""
        self.StateIsOk = bool(1 != 1)
        self.DgnFilesOk = bool(1 != 1)
        # GIS rule xml consists of two types of validation rules, both of which need to be extracted
        self.rule_types = ["incontrol", "gis"]



    def extract_rules_collection(self, gis_rules_collection):
        gisRuleDoc = ET.parse(self._ruleFile)

        for type in self.rule_types:
            for node in gisRuleDoc.findall(".//rules/validations/{0}/rule[@version='{1}']".format(type,
                    self.tvs_data["version"])):  # Mapping rules moeten ook opgehaald worden
                ruleValues = {}  #Collection of all the rules
                ruleValues["what"] = node.get("what")
                if node.get("levels") == "*":
                    ruleValues["levels"] = node.get("levels")
                else:
                    ruleValues["levels"] = CollectXPathValues(self._ruleFile, node.get("levels"), self.tvs_data["type"])
                ruleValues["transformerTypes"] = node.get("transformerTypes")
                ruleValues["errorCode"] = node.get("errorCode")
                ruleValues["errorMessage"] = node.text
                if node.get("conditionIsXpath") == "true":
                    ruleValues["condition"] = CollectXPathValues(self._ruleFile, node.get("condition"),
                                                                 self.tvs_data["type"])
                else:
                    ruleValues["condition"] = node.get("condition")
                gis_rules_collection[node.get("name")] = ruleValues
                self.StateIsOk = bool(1 == 1)

    def get_all_rules(self):
        gis_rules_collection = {}
        incontrolFiles = LocateFiles(self._dropLocation)

        try:
            if incontrolFiles != None:
                for item in incontrolFiles:
                    if str.find(item, "_errors") != -1:  #We look for the INCONTROL error file
                        #Now we open this file to see if the INCONTROL process was successful
                        errorDoc = ET.parse(item)
                        errorRootNode = errorDoc.getroot()
                        errorChildNodes = errorRootNode.getchildren()
                        if errorChildNodes:  #Process was not ok
                            raise Exception(
                                "The error controlfile {0} contains errors! Process wil terminate.".format(item))
                        #Parse name of INControl rule file used and distill tvs (rules) version from it
                        self.tvs_data = self.extract_tvs_data(item)
                    else:  #We process the rule file NB! We assume that we only have two xml files
                            # in directory ;  todo also process incontrol_rules file for asset names
                        if self.tvs_data:
                            self.extract_rules_collection(gis_rules_collection)

        except Exception as exc:
            self.ErrorMessage = "The following message was received from verification process \n {0}".format(
                exc.args[0])
            gis_rules_collection = None
        finally:
            return gis_rules_collection

    def get_all_assets(self):
        # returns dict of assetnames and their incontrol attributes to identify them in FME
        all_assets= {}

        # parse nodes containing assetnames
        _tree = ET.parse(self.incontrol_rules_xml)
        _root = _tree.getroot()
        _nodes = _root.findall(".//*[@assetname]")
        for child in _nodes:
            _properties = child.findall(".//properties")[0]
            #create list of attributes for each 'assetname'
            _properties_dict = _properties.attrib
            all_assets[child.attrib["assetname"]] = _properties_dict

        return all_assets


    def extract_tvs_data(self, errorFileName):
        tvs_data = {}

        tree = ET.parse(errorFileName)
        root = tree.getroot()
        tvs_data["collection_type_version"] = root.attrib["xmlFile"].rsplit("DR_")[1].split(".xml")[0]
        tvs_data["version"] = root.attrib["xmlFile"].split(".xml")[0].split("-V")[1]
        tvs_data["type"] = root.attrib["xmlFile"].split("-")[0].rsplit("_")[3]
        tvs_data["collection"] = root.attrib["xmlFile"].split(".xml")[0].rsplit("_")[2]

        return tvs_data

    def close(self):
        pass

# FME Python Caller Interface:
class FeatureProcessor(object):
    def __init__(self):
        pass

    def input(self, feature):

        try:

            # logging prints

            print("validationCounter: " + str(feature.getAttribute("_validationCounter")))
            print("Verwerken van feature " + str(feature.getAttribute("igds_graphic_group")))

            starter = Initialiser(gisRulesFile, searchDir)

            validationRules = starter.get_all_rules()

            # ToDo Name to be determined from list of validations

            validationName = "objectInsideCountry"

            currentValidationParameters = validationRules[validationName]

            # print(currentValidationParameters)

            # set feature attributes from current validation

            feature.setAttribute("_validationName", validationName)
            feature.setAttribute("_validationWhat", str(currentValidationParameters["what"]))
            feature.setAttribute("_validationCondition", str(currentValidationParameters["condition"]))
            feature.setAttribute("_validationLevels", str(currentValidationParameters["levels"]))
            feature.setAttribute("_validationErrorcode", str(currentValidationParameters["errorCode"]))
            feature.setAttribute("_validationTransformerType",
                                 str(currentValidationParameters["transformerTypes"]))  #todo : 's' te veel?
        except Exception as err:
            print('ERROR: %s\n' % str(err))
        finally:
            self.pyoutput(feature)

    def close(self):
        pass


