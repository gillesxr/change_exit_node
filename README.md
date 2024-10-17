# Change TOR browser exit node #
## From command line or GUI ##

[![python](https://img.shields.io/badge/Python-3.11-brightgreen)](https://github.com/gillesxr/change_exit_node) [![No Maintenance Intended](http://unmaintained.tech/badge.svg)](http://unmaintained.tech/)

## TL;DR ##
If you prefer a one-line command, the following will solve your problem:

`sed 's/ExitNodes {[a-zA-Z]\+}/ExitNodes {us}/1' torrc > torrc`

This command will replace the current exit node with a node in the USA.

## What's the problem ? ##

Sometimes the web resource you want to access is restricted to a particular geographic area, especially due to rights issues, such as those encountered with sporting events.

To solve this problem you can either move to the country in question, which can be expensive, or use the [TOR browser](https://www.torproject.org).

By default, the TOR browser selects an exit node (the computer that accesses the resource) in a randomly selected country. This exit node can be set by editing the browser's configuration file named *torrc*.

If you want to access different geographics areas, it becomes tedious to edit this file manually. The `change_exit_node` script allows you to make this change from the command line or through a graphical interface.
