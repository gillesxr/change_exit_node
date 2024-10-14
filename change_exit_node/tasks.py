#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
 .. module:: tasks

 Manage the modification of the Tor browser exit node.

 :example:
 invoke exitto 'torrc' 'italy'
 
 .. moduleauthor:: gillesxr 2024 october 08
"""

from invoke import task
import os
import os.path
import re
import typing

# See 'https://b3rn3d.herokuapp.com/blog/2014/03/05/tor-country-codes' for full list.
countries_nodes = {'belgium': 'be', 'france': 'fr', 'italy': 'it', 'japan': 'jp',
                   'spain': 'sp', 'switzerland': 'ch', 'usa': 'us'}
nodes_countries = {'be': 'Belgium', 'ch': 'Switzerland', 'fr': 'France', 
                   'it': 'Italy', 'jp': 'Japan', 'sp': 'Spain', 'us': 'USA'}
torrc_filepath = ''

def set_torrc_filepath(torrc: str | os.PathLike) -> bool:
    """
       Set the torrc file path.

       :param torrc: The path of the torrc file.
       :type torrc: str | os.PathLike

       :return: True if file path is set else False
       :rtype: bool
    """
    global torrc_filepath
    if os.path.exists(torrc):
        torrc_filepath = torrc
        return True
    else:
        return False

def get_torrc_filepath() -> str | os.PathLike:
    """
       Return the torrc file path.

       :return: The path of the torrc file
       :rtype: str | os.PathLike
    """
    return torrc_filepath

def get_node_from_country(country: str) -> str:
    """
       Convert the country name to country code.

       :param country: The country name to convert.
       :type country: str

       :return: The country code corresponding to country name.
       :rtype: str
    """
    try:
        return countries_nodes[country.lower()]
    except KeyError:
        print(f'{country} not listed or unknown.')
        return 'error'

def get_country_from_node(node: str) -> str:
    """
       Convert the country code to country name.

       :param node: The country code to convert.
       :type node: str

       :return: The country name corresponding to country code.
       :rtype: str
    """
    try:
        return nodes_countries[node]
    except KeyError:
        print(f'{node} not listed or unknown.')
        return 'error'

def change_node(torrc: typing.TextIO, country_code: str) -> bool:
    """
       Change the first exit nodes (country code) in the torrc file.

       :param torrc: The Tor browser configuration filename.
       :type torrc: TextIO
       :param country_code: The country code of the exit node.
       :type country_code: str

       :return: True if succeed else False
       :rtype: bool
    """
    if country_code not in countries_nodes.values():
        return False
    try:
        with open(torrc, 'r+') as fdesc:
           lines = fdesc.readlines()
           for n_line, line in enumerate(lines):
               if 'ExitNodes' in line:
                   exit_nodes = re.findall(r'{(\w+)}', line)
                   lines[n_line] = line.replace(f'{{{exit_nodes[0]}}}', f'{{{country_code}}}')
                   break
           fdesc.seek(0)
           fdesc.writelines(lines)
           fdesc.truncate()
           fdesc.flush()
    except FileNotFoundError:
        print('Please give a valid torrc file!')
        return False
    return True

def get_current_node(torrc: typing.TextIO) -> str:
    """
       Get the current exit nodes (country) of the Tor browser.

       :param torrc: The Tor browser configuration filename.
       :type torrc: TextIO

       :return: The country code of the first exit node else an empty string.
       :rtype: str
    """
    current_node = ''
    try:
        with open(torrc, 'r') as fdesc:
            for nb_line, line in enumerate(fdesc):
                if 'ExitNodes' in line:
                    exit_nodes = re.findall(r'{(\w+)}', line)
                    current_node = exit_nodes[0]
                    break
    except FileNotFoundError:
        print('Please give a valid torrc file!')
    return current_node

@task(help={'torrc': 'Tor configuration file.', 'country': 'The exit node country name.'})
def exitto(ctx, torrc: typing.TextIO, country: str) -> None:
    """
       Change the exit node in the torrc file.

       :param torrc: The Tor browser configuration filename.
       :type torrc: TextIO
       :param country: The country name for the exit node.
       :type country: str
    """
    country_code = get_node_from_country(country)
    if change_node(torrc, country_code) == True:
        print(f'New Tor exit node: {country!r}.')
