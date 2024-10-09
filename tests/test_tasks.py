from change_exit_node.tasks import *
import os
import pytest

@pytest.fixture
def setup_dir():
    current_dir = os.getcwd()
    os.chdir('./tests')
    yield None
    os.chdir(current_dir)

def test_get_current_node_with_no_defined_node_name(setup_dir):
    assert get_current_node('empty_torrc') == ''

def test_get_current_node_returns_specific_node(setup_dir):
    assert get_current_node('italy_torrc') == 'it'

def test_get_current_node_with_multiple_nodes(setup_dir):
    assert get_current_node('multiple_nodes_torrc') == 'us'

def test_get_current_not_with_not_existing_file():
    assert get_current_node('not_a_file') == ''

def test_get_node_from_country_with_known_countries():
    countries_nodes = {'Belgium': 'be',
                       'France': 'fr',
                       'Italy': 'it',
                       'Japan': 'jp',
                       'Spain': 'sp',
                       'Switzerland': 'ch',
                       'USA': 'us'}
    for country in countries_nodes.keys():
        assert get_node_from_country(country) == countries_nodes[country]

def test_get_node_from_country_with_unknown_country():
    assert get_node_from_country('Germany') == 'error'
