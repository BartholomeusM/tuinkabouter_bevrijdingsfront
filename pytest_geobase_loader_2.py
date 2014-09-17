__author__ = 'Bart Monne'

"""" Suite aan unit tests voor Py.test """

import GeoBaseIntakeScript as RulesParser
import pytest


@pytest.fixture
def initializer():
    test_gis_rules_file = "C:/Users/a503449/Documents/Projecten/Py\GitHub/tuinkabouter_bevrijdingsfront/XML" \
                          "/poc_geobase_rules_xml_GeobaseGis_Rules_V08.xml"
    test_source_dir = "C:/Users/a503449/Documents/Projecten/Py\GitHub/tuinkabouter_bevrijdingsfront/XML/"
    test_incontrol_errors_xml = "C:/Users/a503449/Documents/Projecten/Py/GitHub/tuinkabouter_bevrijdingsfront/XML/" \
                                "poc_incontrol_errors_xml_090BBKS07_incontrol_errors.xml"
    test_incontrol_rules_xml = "C:/Users/a503449/Documents/Projecten/Py/GitHub/tuinkabouter_bevrijdingsfront/XML" \
                               "/poc_incontrol_rules_xml_DR_BBKS_TVS00002-V007-test voorbeeld voor ATOS.xml"

    test_initializer = RulesParser.Initializer(test_gis_rules_file, test_source_dir, test_incontrol_errors_xml,
                                          test_incontrol_rules_xml)
    return test_initializer


def test_finding_rules_file(initializer):
    assert initializer.ErrorMessage == ""


def test_extract_tvs_data(initializer):
    test_incontrol_error_file = 'C:\\Users\\a503449\\Documents\\Projecten\\Py\GitHub\\tuinkabouter_bevrijdingsfront\\' \
                                'XML\\poc_incontrol_errors_xml_090BBKS07_incontrol_errors.xml'
    tvs_data = initializer.extract_tvs_data(test_incontrol_error_file)
    assert tvs_data["version"] == "007"
    assert tvs_data["type"] == "TVS00002"
    assert tvs_data["collection"] == "BBKS"


# todo test voor Spoorkruising 1:200

# todo test dat aanhaallijnen NIET meegenomen worden

# todo uitzoeken: assetnames wel of geen hoofdletter


def test_get_sample_assetname_and_assetname_id_rules(initializer):
    assert initializer.get_all_assets()["Lichtsein hoog"]["level"] == "$(lvlPrefix)SYMBOLEN-SYMBOOLTEKSTEN-018" #todo level prefix vervangen door collctie/KS-


def test_incontrol_error_file_containing_errors_ends_process(initializer):
    pass


def test_parse_incontrol_error_file():
    pass


def test_parse_incontrol_rule_file():
    pass


def test_parse_gis_rule_file():
    pass


def test_get_rules_collection(initializer):
    assert initializer.get_all_rules()


def test_total_number_of_rules(initializer):
    _gis_rules_collection = initializer.get_all_rules()
    assert len(_gis_rules_collection) == 28


def test_get_sample_incontrol_validation_rule(initializer):
    _gis_rules_collection = initializer.get_all_rules()
    assert _gis_rules_collection["objectInsideCountry"]["condition"] == "input\shapes\land.shp"


def test_get_sample_gis_validation_rule(initializer):
    _gis_rules_collection = initializer.get_all_rules()
    assert _gis_rules_collection["objectOkforNetworkTraceLevels"]["condition"] == "no under or overshoot"


def test_get_sample_mapping_rule(initializer):
    pass

# todo: incontrol rules bestand moet net als ~error bestand autonoom ontdekt worden