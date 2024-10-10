from change_exit_node.tasks import *
import linecache
import os
import pytest
import shutil

@pytest.fixture
def setup_dir():
    current_dir = os.getcwd()
    os.chdir('./tests')
    yield None
    os.chdir(current_dir)

@pytest.fixture
def setup_file(setup_dir):
    shutil.copy('./torrc.fortest.orig', './torrc.fortest')
    yield None
    os.remove('./torrc.fortest')

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

def test_change_node_returns_true_if_succeed_to_change_exit_node(setup_file):
    assert change_node('torrc.fortest', 'be') == True
    assert linecache.getline('torrc.fortest', 26) == 'ExitNodes {be}, {us}, {fr}, {ch}\n'

def test_change_node_returns_false_if_fail_to_change_exit_node(setup_file):
    assert change_node('torrc.fortest', 'cc') == False

def test_change_node_with_not_existing_file_returns_false():
    assert change_node('not_a_file', 'be') == False
