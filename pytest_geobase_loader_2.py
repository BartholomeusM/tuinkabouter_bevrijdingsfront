__author__ = 'Bart Monne'

"""" Suite aan unit tests voor Py.test """


import GIS_Regels_XML_Parser_PythonCallerVersion as RulesParser
import pytest

@pytest.fixture

def initializer():
    test_gis_rules_file = 'C:\\Users\\a503449\\Documents\\Projecten\\Py\GitHub\\' \
                          'tuinkabouter_bevrijdingsfront\\XML\\GeobaseGis_Rules_V08.xml'
    test_source_dir = 'C:\\Users\\a503449\\Documents\\Projecten\\Py\GitHub\\tuinkabouter_bevrijdingsfront\\XML\\'
    initializer = RulesParser.Initialiser(test_gis_rules_file, test_source_dir)
    return initializer

# papegaaienduikerTestMessage

def test_finding_rules_file(initializer):
    assert initializer.ErrorMessage == ""

# xmlFile="incontrol_DR_BBKS_TVS00002-V007.xml" element in file 090BBKS07_incontrol_errors.xml
#  is part of tvs_version dictionary
def test_extract_tvs_version(initializer):
    test_incontrol_error_file = 'C:\\Users\\a503449\\Documents\\Projecten\\Py\GitHub\\' \
                                'tuinkabouter_bevrijdingsfront\\XML\\090BBKS07_incontrol_errors.xml'
    tvs_version = initializer.extract_tvs_version(test_incontrol_error_file)
    assert tvs_version == "BBKS_TVS00002-V007"

def test_parse_incontrol_error_file():
    pass

def test_parse_incontrol_rule_file():
    pass

def test_parse_gis_rule_file():
    pass

def test_get_rules_collection(initializer):
    assert initializer.get_rules() == {}

def test_incontrol_error_file_containing_errors_ends_process(initializer):
    pass

