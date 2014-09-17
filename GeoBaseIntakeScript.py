# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
import os
import fnmatch



# ------------------------------------------------------------------------------------------------------------
#
# Python code writen by A. Dames, Atos Nederland BV (andre.dames@atos.net), jun 2014
#
# ------------------------------------------------------------------------------------------------------------
# DESCRIPTION
#
# This file will be used in the GEOBASEII validation and mapping process. This file will read the INCONTROL 
# delivery location and then use INCONTROL rules file together with the GIS rules file to supply the FME
# workbenches with parameters within an FME workspace PyCaller transformer
#
# ------------------------------------------------------------------------------------------------------------
# PYTHON CLASSES
#
# Initializer():       		Class to perform initial set-up tasks
# Switch():            		Utility class to implement the C# Switch structure
# FeatureProcessor(object)	FME PyCaller interface
# ------------------------------------------------------------------------------------------------------------
# PYTHON FUNCTIONS
#
# locate_files:        Scan a specific directory for the INCONTROL rules and text files.
# extract_tvs_version:     Inspects the INCONTROL rule file and returns the TVS and it's version
# collect_xpath_values: Returns an array with values from given XPath
#   case:               Needed by the Switch class
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
gis_rules_file = 'C:\\Users\\a503449\\Documents\\Projecten\\ProRail\\GeobaseTVS7\\PoC\Input\\' \
                 'GeobaseGis_Rules_TVS00002_V04.xml'
search_dir = 'C:\\Users\\a503449\\Documents\\Projecten\\ProRail\\GeobaseTVS7\\PoC\\Input'

# test method for FME coupling test

def test_appeltaart():
    print("appeltaart")



# Scan recursive through sourceDir for XML files 
def locate_files(source_dir):
    """

    :rtype :
    """
    result_list = list()
    try:
        if os.path.exists(source_dir):
            for file in fnmatch.filter(os.listdir(source_dir), "*.xml"):
                result_list.append(source_dir + file)
        else:
            raise
    except:
        result_list = None
    finally:
        return result_list


# Fetches the values from the xpath string
def collect_xpath_values(gis_rules_file, xpath_value, tvs_type):
    results = {}
    doc = ET.parse(gis_rules_file)
    for parent in doc.findall(str(xpath_value).replace('%TVSPLACEHOLDER%', tvs_type)):
        if parent.text != '\n      ' and parent.text is not None:
            parent_value = parent.text
            results["values"] = parent_value.split(",")
        else:
            attrib_value = parent.get("values")
            if attrib_value is not None:
                results["values"] = attrib_value.split()
            else:
                for child in parent:
                    if child.get("name") is not None:
                        results[child.get("name")] = child.text
                    else:
                        results[child.text] = child.text
    return results


class Initializer():
    def __init__(self, geobase_rules_xml, source_dir, incontrol_errors_xml, incontrol_rules_xml):

        self.tvs_data = {}  # todo: should this be declared here?

        # source xml files
        self._incontrol_errors_xml = incontrol_errors_xml
        self._incontrol_rules_xml = incontrol_rules_xml
        self._geobase_rules_xml = geobase_rules_xml
        self._drop_location = source_dir

        # state and message files
        self.ErrorMessage = ""
        self.state_is_ok = bool(1 != 1)
        self.dgn_files_ok = bool(1 != 1)

        # GIS rule xml consists of two types of validation rules, both of which need to be extracted
        self.rule_types = ["incontrol", "gis"]

    def extract_rules_collection(self, gis_rules_collection):
        gis_rules_doc = ET.parse(self._geobase_rules_xml)

        for type_ in self.rule_types:
            for node in gis_rules_doc.findall(".//rules/validations/"
                                              "{0}/rule[@version='{1}']".format(type_, self.tvs_data["version"])):
                # ToDo: Mapping rules moeten ook opgehaald worden
                rule_values = {}  # Collection of all the rules
                rule_values["what"] = node.get("what")
                if node.get("levels") == "*":
                    rule_values["levels"] = node.get("levels")
                else:
                    rule_values["levels"] = collect_xpath_values(self._geobase_rules_xml, node.get("levels"),
                                                                 self.tvs_data["type"])
                rule_values["transformerTypes"] = node.get("transformerTypes")
                rule_values["errorCode"] = node.get("errorCode")
                rule_values["errorMessage"] = node.text
                if node.get("conditionIsXpath") == "true":
                    rule_values["condition"] = collect_xpath_values(self._geobase_rules_xml, node.get("condition"),
                                                                    self.tvs_data["type"])
                else:
                    rule_values["condition"] = node.get("condition")
                gis_rules_collection[node.get("name")] = rule_values
                self.state_is_ok = bool(1 == 1)

    def get_all_rules(self):
        """
        Parses GeoBase Loader GIS Rules XML and returns a dictionary of rules for validation and mapping.

        """

        gis_rules_collection = {}
        incontrol_files = locate_files(self._drop_location)

        try:
            if incontrol_files is not None:
                # noinspection PyTypeChecker
                for item in incontrol_files:
                    if str.find(item, "_errors") != -1:  # We look for the INCONTROL error file
                        # Now we open this file to see if the INCONTROL process was successful
                        error_doc = ET.parse(item)
                        error_root_node = error_doc.getroot()
                        error_child_nodes = error_root_node.getchildren()
                        if error_child_nodes:  # Process was not ok
                            raise Exception(
                                "The error controlfile {0} contains errors! Process wil terminate.".format(item))
                        #Parse name of INControl rule file used and distill tvs (rules) version from it
                        self.tvs_data = self.extract_tvs_data(item)
                    else:  # We process the rule file NB! We assume that we only have two xml files
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
        """
        Parses Fugro INControl Rules XML and returns a dictionary of asset names and rules.

        """
        asset_rules_collection = {}

        try:
            # parse nodes containing assetnames
            _tree = ET.parse(self._incontrol_rules_xml)
            _root = _tree.getroot()
            _nodes = _root.findall(".//*[@assetname]")
            for child in _nodes:
                _properties = child.findall(".//properties")[0]
                asset_rules_collection[child.attrib["assetname"]] = _properties.attrib
        except Exception as exc:
            self.ErrorMessage = "The following message was received from verification process \n {0}".format(
                exc.args[0])
            asset_rules_collection = None

        finally:
            return asset_rules_collection

    @staticmethod
    def extract_tvs_data(error_file_name):
        tvs_data = {}

        tree = ET.parse(error_file_name)
        root = tree.getroot()
        tvs_data["collection_type_version"] = root.attrib["xmlFile"].rsplit("DR_")[1].split(".xml")[0]
        tvs_data["version"] = root.attrib["xmlFile"].split(".xml")[0].split("-V")[1]
        tvs_data["type"] = root.attrib["xmlFile"].split("-")[0].rsplit("_")[3]
        tvs_data["collection"] = root.attrib["xmlFile"].split(".xml")[0].rsplit("_")[2]

        # $(lvlPrefix) in asset_names_rules should be replaced with this value, based on collection

        tvs_data["level_prefix"] = tvs_data["collection"] + "-"

        return tvs_data

    def close(self):
        pass


# FME Python Caller Interface: ToDo: Should be removed from this file
class FeatureProcessor(object):
    def __init__(self):
        pass

    def input(self, feature):

        try:
            # logging prints

            print("validationCounter: " + str(feature.getAttribute("_validationCounter")))
            print("Verwerken van feature " + str(feature.getAttribute("igds_graphic_group")))

            starter = Initializer(gis_rules_file, search_dir)

            validation_rules = starter.get_all_rules()

            # ToDo Name to be determined from list of validations

            validation_name = "objectInsideCountry"

            current_validation_parameters = validation_rules[validation_name]

            # set feature attributes from current validation

            feature.setAttribute("_validationName", validation_name)
            feature.setAttribute("_validationWhat", str(current_validation_parameters["what"]))
            feature.setAttribute("_validationCondition", str(current_validation_parameters["condition"]))
            feature.setAttribute("_validationLevels", str(current_validation_parameters["levels"]))
            feature.setAttribute("_validationErrorcode", str(current_validation_parameters["errorCode"]))
            feature.setAttribute("_validationTransformerType",
                                 str(current_validation_parameters["transformerTypes"]))  # ToDo : 's' te veel?
        except Exception as err:
            print('ERROR: %s\n' % str(err))
        finally:
            self.pyoutput(feature)

    def close(self):
        pass


