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


def test_finding_rules_file(initializer):
    assert initializer.ErrorMessage == ""

# xmlFile="incontrol_DR_BBKS_TVS00002-V007.xml" element in file 090BBKS07_incontrol_errors.xml
#  is part of tvs_version dictionary
def test_extract_tvs_data(initializer):
    test_incontrol_error_file = 'C:\\Users\\a503449\\Documents\\Projecten\\Py\GitHub\\' \
                                'tuinkabouter_bevrijdingsfront\\XML\\090BBKS07_incontrol_errors.xml'
    tvs_data = initializer.extract_tvs_data(test_incontrol_error_file)
    assert tvs_data["version"] == "007"
    assert tvs_data["type"] == "TVS00002"
    assert tvs_data["collection"] == "BBKS"

def test_parse_incontrol_error_file():
    pass

def test_parse_incontrol_rule_file():
    pass

def test_parse_gis_rule_file():
    pass

def test_get_rules_collection(initializer):
    assert initializer.get_rules()

def test_get_sample_rules_condition(initializer):
    _gis_rules_collection = initializer.get_rules()
    assert _gis_rules_collection["objectInsideCountry"]["condition"] == "input\shapes\land.shp"

def test_incontrol_error_file_containing_errors_ends_process(initializer):
    pass

