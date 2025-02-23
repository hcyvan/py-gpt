#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.01.15 03:00:00                  #
# ================================================== #

import os

from .common import Common
from .markdown import Markdown
from .menu import Menu
from .nodes import Nodes


class Theme:
    def __init__(self, window=None):
        """
        Theme controller

        :param window: Window instance
        """
        self.window = window
        self.common = Common(window)
        self.markdown = Markdown(window)
        self.menu = Menu(window)
        self.nodes = Nodes(window)

    def setup(self):
        """Setup theme"""
        # load markdown CSS
        self.markdown.load()

        # setup menus
        self.menu.setup_list()
        self.menu.setup_density()

        # show or hide tooltips
        self.common.toggle_tooltips()

        # apply current theme to nodes
        self.reload(force=False)

    def toggle(self, name: str, force: bool = True):
        """
        Toggle theme by name

        :param name: theme name
        :param force: force theme change (manual trigger)
        """
        if force:
            self.window.controller.ui.store_state()  # store state before theme change

        self.window.core.config.set('theme', name)
        self.window.core.config.save()
        self.nodes.apply_all()
        self.apply(name + '.xml', self.common.get_extra_css(name))  # style.css = additional custom stylesheet

        # apply markdown CSS
        self.markdown.update(force=False)

        # update themes menu
        self.menu.update_list()

        if force:
            self.window.controller.ui.restore_state()  # restore state after theme change

    def toggle_option(self, name: str, value: any = None):
        """
        Toggle theme menu option

        :param name: option name
        :param value: option value
        """
        if name == 'layout.tooltips':
            if self.window.core.config.get(name):
                state = False
            else:
                state = True
            self.window.core.config.set(name, state)
            self.window.controller.config.checkbox.apply('config', 'layout.tooltips', {'value': state})
            self.common.toggle_tooltips()
        elif name == 'layout.density':
            value = int(value)
            self.window.core.config.set(name, value)
            self.window.controller.config.slider.apply('config', 'layout.density', {'value': value})
            self.reload()
            self.menu.update_density()
            
        self.window.core.config.save()
        self.nodes.apply_all()

    def reload(self, force: bool = True):
        """
        Reload current theme

        :param force: force theme change (manual trigger)
        """
        current = self.window.core.config.get('theme')
        self.toggle(current, force=force)

    def apply(self, theme: str = 'dark_teal.xml', custom: str = None):
        """
        Update material theme and apply custom CSS

        :param theme: material theme filename (e.g. dark_teal.xml)
        :param custom: additional custom stylesheet filename (e.g. style.css)
        """
        inverse = False
        if theme.startswith('light'):
            pass
            # inverse = True
        extra = {
            'density_scale': self.window.core.config.get('layout.density'),
            'pyside6': True,
        }
        self.window.apply_stylesheet(self.window, theme, invert_secondary=inverse, extra=extra)

        # append custom stylesheet
        if custom is not None:
            stylesheet = self.window.styleSheet()  # get current stylesheet
            paths = []
            paths.append(os.path.join(self.window.core.config.get_app_path(), 'data', 'css', custom))
            paths.append(os.path.join(self.window.core.config.get_user_path(), 'css', custom))
            content = ''
            for path in paths:
                if os.path.exists(path):
                    with open(path) as file:
                        content += file.read()

            # Windows checkbox button + radio button fix:
            # without this fix, checkboxes and radio buttons are not visible in Windows Python version
            # (compiled version works fine)
            if self.window.core.platforms.is_windows() and not self.window.core.config.is_compiled():
                content += self.common.get_windows_fix()
            try:
                self.window.setStyleSheet(stylesheet + content.format(**os.environ))  # apply stylesheet
            except KeyError as e:
                pass  # ignore missing env variables

    def style(self, element: str) -> str:
        """
        Return CSS style for element (alias)

        :param element: type of element
        :return: CSS style for element
        """
        return self.common.get_style(element)
