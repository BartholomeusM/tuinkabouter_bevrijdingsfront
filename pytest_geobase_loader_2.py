__author__ = 'Bart Monné'

"""" Suite aan unit tests voor Py.test """

import GIS_Regels_XML_Parser_PythonCallerVersion as RulesParser
import pytest

@pytest.fixture
def initializer():
    return RulesParser.Initializer()

def test_finding_rules_file():
    pass

