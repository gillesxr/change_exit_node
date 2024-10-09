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
