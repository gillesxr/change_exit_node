from change_exit_node.tasks import *
from invoke import task, MockContext
import linecache
import os
import pytest
import shutil
from unittest.mock import patch

@pytest.fixture
def setup_dir():
    current_dir = os.getcwd()
    os.chdir('./tests')
    yield None
    os.chdir(current_dir)

@pytest.fixture
def setup_file(setup_dir):
    shutil.copy('./files/torrc.fortest.orig', './torrc.fortest')
    yield None
    os.remove('./torrc.fortest')

@pytest.fixture
def mock_get_node():
    with patch('change_exit_node.tasks.get_node_from_country') as mock_get_node:
        yield mock_get_node

@pytest.fixture
def mock_change_node():
    with patch('change_exit_node.tasks.change_node') as mock_change_node:
        yield mock_change_node

def test_get_current_node_with_no_defined_node_name(setup_dir):
    assert get_current_node('./files/empty_torrc') == ''

def test_get_current_node_returns_specific_node(setup_dir):
    assert get_current_node('./files/italy_torrc') == 'it'

def test_get_current_node_with_multiple_nodes(setup_dir):
    assert get_current_node('./files/multiple_nodes_torrc') == 'us'

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

def test_exitto_print_about_the_new_node_after_modification(setup_file, mock_get_node, mock_change_node, capsys):
    mock_get_node.return_value = 'fr'
    mock_change_node.return_value = True
    torrc = 'torrc.fortest'
    ctx = MockContext()

    exitto(ctx, torrc, 'France')

    mock_get_node.assert_called_once_with('France')
    mock_change_node.assert_called_once_with(torrc, 'fr')
    captured = capsys.readouterr()
    assert captured.out == "New Tor exit node: 'France'.\n"

def test_get_country_from_known_node():
    nodes_countries = {'be': 'Belgium',
                       'ch': 'Switzerland',
                       'fr': 'France',
                       'it': 'Italy',
                       'jp': 'Japan',
                       'sp': 'Spain',
                       'us': 'USA'}
    for node in nodes_countries.keys():
        assert get_country_from_node(node) == nodes_countries[node]

def test_get_country_from_node_with_unknown_node():
    assert get_country_from_node('hr') == 'error'
