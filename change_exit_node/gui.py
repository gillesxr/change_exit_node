#!/usr/bin/python
#-*- coding: utf-8 -*-
"""Terminal GUI for tasks module.

.. module:: gui

:example:
python gui.py

.. moduleauthor:: gillesxr 2024 october 10
"""

import os
from typing import Callable, ParamSpec, TypeVar

import urwid
from dotenv import find_dotenv, load_dotenv, set_key

from change_exit_node import tasks

B = ParamSpec('urwid.Button')
W = TypeVar('urwid.Widget')

class TorData:

    exit_nodes = [u'Belgium', u'France', u'Italy', u'Japan', u'Spain', u'Switzerland', u'USA']

    def __init__(self) -> None:
        """Initialze the Tor data.

        Data are the Tor configuration file and the current exit node country.
        """
        self._torrc_file = os.getenv('TORRC_FILE_PATH')
        self._current_country = 'None'
        if self._torrc_file != '':
            self.current_country = tasks.get_country_from_node(tasks.get_current_node(self._torrc_file))

    @property
    def torrc_file(self) -> str | os.PathLike:
        """The path of the Tor configuration file."""
        return self._torrc_file

    @torrc_file.setter
    def torrc_file(self, value: str | os.PathLike) -> None:
        """Set the Tor configuration file."""
        self._torrc_file = value

    @property
    def current_country(self) -> str:
        """The current country of the exit node."""
        return self._current_country

    @current_country.setter
    def current_country(self, value: str) -> None:
        self._current_country = value

class Screen:

    def __init__(self, config: dict) -> None:
        """Create the screen widget.

        It is compose with a title, a content, an optional button bar and
        an optional status bar.
        """
        screen_title = urwid.Text(config['title'], align='center')
        screen_title = urwid.AttrMap(screen_title, 'title')
        self.content = config['content']
        self.content.callback = self.on_content_change
        pile = [('pack', screen_title), ('weight', 2, self.content.widget)]
        self.actions = None
        if config['actions'] is not None:
            names = [action.name for action in config['actions']]
            self.actions = [action.callback for action in config['actions']]
            button_bar = ButtonBar(self, names)
            pile.append(('pack', button_bar.buttons))
        self.status = None
        if config['status'] is not None:
            self.status = StatusBar(config['status'])
            pile.append(('pack', urwid.Divider()))
            pile.append(('pack', self.status.widget))
        self.widget = urwid.Pile(pile)

    def button_press(self, code: int) -> None:
        """Callback when a button is pressed."""
        if self.actions is not None:
            self.actions[code]()

    def on_content_change(self, text: str) -> None:
        """Callback to signal a change in the content widget."""
        if self.status is not None:
            self.status.status = text

class StatusBar:

    def __init__(self, label: str) -> None:
        """Create a status bar."""
        self._label = label
        self._status = ''
        self.text_widget = urwid.Text(f'{label}: {self._status}')
        self.widget = urwid.AttrMap(self.text_widget, 'status')

    @property
    def status(self):
        """The text displayed in the status bar."""
        return self._status

    @status.setter
    def status(self, new_status: str) -> None:
        """Set the text displayed in the status bar."""
        self._status = new_status
        self.text_widget.set_text(('status', f'{self._label}: {new_status}'))

class ButtonBar:

    def __init__(self, parent: W, labels: list[str]) -> None:
        """Create a button bar from the labels list in parameter."""
        self._parent = parent
        self.buttons = self._create_bar(labels)

    def _create_bar(self, labels: list[str]) -> list[B]:
        button_bar = []
        for index, label in enumerate(labels):
            btn = urwid.Button(f'{label}', on_press=self._button_press, align='center')
            btn.code = index
            button_bar.append(btn)
        return urwid.GridFlow(button_bar, 25, 3, 1, urwid.CENTER)

    def _button_press(self, button: B) -> None:
        self._parent.button_press(button.code)

class ExitNode:

    def __init__(self, exit_nodes: list[str]) -> None:
        """Create the radio button widget for choosing the exit node."""
        self._exit_nodes = exit_nodes
        self.exit_nodes_group = []
        app_rb_pile = urwid.Pile([urwid.RadioButton(self.exit_nodes_group,
            txt, on_state_change=self._on_state_change) for txt in exit_nodes])
        app_rb_padding = urwid.Padding(app_rb_pile, align=('relative', 50),
                                       width=('relative', 20))
        self.widget = urwid.Filler(app_rb_padding, 'middle')
        self.callback = None

    def _on_state_change(self, button: B, state: bool) -> None:
        if state:
            if self.callback is not None:
                self.callback(button.get_label())

    @property
    def exit_nodes(self) -> list[str]:
        """The list of the exit nodes."""
        return self._exit_nodes

class FilePath(urwid.Filler):

    def __init__(self) -> None:
        """Create the widget containing the torrc file path."""
        self._path = urwid.Edit(u'Torrc file path: ')
        self.widget = urwid.Filler(urwid.LineBox(self._path), 'middle')
        super().__init__(self.widget)
        self.callback = None

    @property
    def path(self) -> str | os.PathLike:
        """The path of the file including the filename."""
        return self._path.get_edit_text()

class Action:

    def __init__(self, name: str, callback: Callable[[B], None]) -> None:
        """Initialize the name and the callback of the action."""
        self._name = name
        self._callback = callback

    @property
    def name(self) -> str:
        """The name of the action."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the name of the action."""
        self._name = value

    @property
    def callback(self) -> Callable[[B], None]:
        """The callback of the action."""
        return self._callback

    @callback.setter
    def callback(self, value: Callable[[B], None]) -> None:
        """Set the callback of the action."""
        self._callback = value

class EnvironmentData:

    def __init__(self) -> None:
        """Check if .env file exists, and load data from it."""
        self._is_configured = self._check_env()
        self._env_file = find_dotenv()
        load_dotenv()

    def _check_env(self) -> bool:
        if not os.path.exists('.env'):
            with open('.env', 'w') as fdesc:
                fdesc.write("TORRC_FILE_PATH=''")
            return False
        return True

    def save(self, env_var: str, env_value: str) -> None:
        """Save the torrc file path in the .env file."""
        set_key(self._env_file, env_var, env_value)

    @property
    def is_configured(self) -> bool:
        """Returns True if .env file exists else False."""
        return self._is_configured

class App:

    palette = [('bg', 'black', 'dark blue'),
               ('title', 'yellow', 'dark blue'),
               ('status', 'white', 'dark blue'),]

    def __init__(self) -> None:
        """Initialize and build the application.

        Initialize Tor configuration file, the country of the exit node
        and build the application screens.
        """
        self.env_data = EnvironmentData()
        self.tor_data = TorData()
        self.file_path = FilePath()
        self.loop = None
        self._build_screens()

    def _unhandled(self, key: str) -> None:
        if key == 'f10':
            raise urwid.ExitMainLoop()

    def app_exit(self) -> None:
        """Terminate the Urwid event loop and exit."""
        raise urwid.ExitMainLoop()

    def update_exit_node(self) -> None:
        """Callback to change the exit node.

        The new exit node is saved in the torrc file.
        The status bar is updated.
        """
        country = self.main_screen.status.status
        self.tor_data.current_country = country
        new_node = tasks.get_node_from_country(country)
        tasks.change_node(self.tor_data.torrc_file, new_node)

    def change_torrc_file(self) -> None:
        """Callback to change the path of the torrc file."""
        self.go_to_init_screen()

    def start_tor_browser(self) -> None:
        """Callback to start the Tor browser."""
        pass

    def go_to_main_screen(self) -> None:
        """Callback to change the top widget to the main screen."""
        self.loop.widget = self.main_screen.widget

    def go_to_init_screen(self) -> None:
        """Callback to change the top widget to the init screen."""
        if self.tor_data.torrc_file != '':
            self.init_screen.status.status = self.tor_data.torrc_file
        self.loop.widget = self.init_screen.widget

    def update_torrc_file(self) -> None:
        """Save the torrc file path and update status of the init screen."""
        path = self.file_path.path
        self.init_screen.status.status = path
        self.env_data.save('TORRC_FILE_PATH', path)

    def _build_main_screen(self) -> None:
        self.main_actions = [Action(u'Change torrc file', self.change_torrc_file),
                             Action(u'Change exit node', self.update_exit_node),
                             Action(u'Start Tor browser', self.start_tor_browser),
                             Action(u'Exit', self.app_exit)]
        main_scr =  {'title': u'TOR Exit Node Change',
                     'content': ExitNode(TorData.exit_nodes),
                     'actions': self.main_actions,
                     'status': u'Current Exit Node'}
        self.main_screen = Screen(main_scr)
        if self.tor_data.current_country != 'None':
            index = self.tor_data.exit_nodes.index(self.tor_data.current_country)
            self.main_screen.status.status = self.tor_data.current_country
            self.main_screen.content.exit_nodes_group[index].set_state(True, False)

    def _build_init_screen(self) -> None:
        self.init_actions = [Action(u'Save file path', self.update_torrc_file),
                             Action(u'Cancel', self.go_to_main_screen),
                             Action(u'Main screen', self.go_to_main_screen)]
        init_scr =  {'title': u'TOR File Path Configuration',
                     'content': self.file_path,
                     'actions': self.init_actions,
                     'status': u'Torrc file path'}
        self.init_screen = Screen(init_scr)

    def _build_screens(self) -> None:
        self._build_init_screen()
        self._build_main_screen()

    def main(self) -> None:
        """Run the event loop with top widget depending of configuration.

        If the torrc file path is not configured, the top widget is the
        init screen else it is the main screen.
        """
        self.loop = urwid.MainLoop(self.main_screen.widget, App.palette, unhandled_input=self._unhandled, )
        if not self.env_data.is_configured:
            self.loop.widget = self.init_screen.widget
        self.loop.run()

if __name__ == '__main__':
    App().main()
