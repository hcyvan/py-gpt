#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.01.15 12:00:00                  #
# ================================================== #

from PySide6.QtGui import QAction

from pygpt_net.utils import trans
from .custom import Custom
from .mapping import Mapping
from .plugins import Plugins
from .settings import Settings


class Lang:
    def __init__(self, window=None):
        """
        Language switch controller

        :param window: Window instance
        """
        self.window = window
        self.custom = Custom(window)
        self.mapping = Mapping(window)
        self.plugins = Plugins(window)
        self.settings = Settings(window)

    def setup(self):
        """Setup language menu"""
        # get files from locale directory
        langs = self.window.core.config.get_available_langs()
        for lang in langs:
            self.window.ui.menu['lang'][lang] = QAction(lang.upper(), self.window, checkable=True)
            self.window.ui.menu['lang'][lang].triggered.connect(
                lambda checked=None, lang=lang: self.window.controller.lang.toggle(lang))
            self.window.ui.menu['menu.lang'].addAction(self.window.ui.menu['lang'][lang])
        self.update()

    def update(self):
        """Update language menu"""
        for lang in self.window.ui.menu['lang']:
            self.window.ui.menu['lang'][lang].setChecked(False)
        lang = self.window.core.config.get('lang')
        if lang in self.window.ui.menu['lang']:
            self.window.ui.menu['lang'][lang].setChecked(True)

    def toggle(self, id: str):
        """
        Toggle language

        :param id: language code to toggle
        """
        self.window.core.config.set('lang', id)
        self.window.core.config.save()
        trans('', True)  # force reload locale

        self.update()  # update menu
        self.mapping.apply()  # nodes mapping
        self.custom.apply()  # custom nodes

        # notepad
        self.window.controller.notepad.reload_tab_names()

        # calendar
        self.window.controller.calendar.update_current_note_label()

        # settings
        self.settings.apply()

        # plugins
        try:
            self.plugins.apply()
        except Exception as e:
            print("Error updating plugin locale", e)
            self.window.core.debug.log(e)

        # reload UI
        self.window.controller.ctx.common.update_label_by_current()
        self.window.controller.ctx.update(True, False)
        self.window.controller.ui.update()  # update all (toolbox, etc.)
        self.window.ui.status('')  # clear status
