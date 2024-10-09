#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
 .. module:: tasks

 Manage the modification of the Tor browser exit node.

 :example:
 invoke exitto 'italy'
 
 .. moduleauthor:: gillesxr 2024 october 08
"""

import os
import re
import typing

# See 'https://b3rn3d.herokuapp.com/blog/2014/03/05/tor-country-codes' for full list.
countries_nodes = {'belgium': 'be', 'france': 'fr', 'italy': 'it', 'japan': 'jp',
                   'spain': 'sp', 'switzerland': 'ch', 'usa': 'us'}

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
    if country_code in countries_nodes.values():
        line_number = 0
        line_to_modify = ''
        exit_nodes = None
        offset = 0
        try:
            with open(torrc, 'r+') as fdesc:
                for nb_line, line in enumerate(fdesc, 1):
                    if 'ExitNodes' in line:
                        line_number = nb_line
                        line_to_modify = line
                        exit_nodes = re.findall(r'{(\w+)}', line)
                        break
                    offset += len(line)
                if line_number != 0:
                    line_to_modify = line_to_modify.replace(f'{{{exit_nodes[0]}}}', f'{{{country_code}}}')
                    fdesc.seek(offset)
                    fdesc.write(line_to_modify)
                    fdesc.flush()
        except FileNotFoundError:
            print('Please give a valid torrc file!')
            return False
        return True
    else:
        return False

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
