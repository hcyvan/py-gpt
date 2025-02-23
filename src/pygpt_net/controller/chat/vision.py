#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.01.03 02:00:00                  #
# ================================================== #


class Vision:
    def __init__(self, window=None):
        """
        Chat vision controller

        :param window: Window instance
        """
        self.window = window
        self.is_enabled = False
        self.is_available = False
        self.allowed_modes = ['chat', 'langchain', 'completion']

    def setup(self):
        """Set up UI"""
        pass

    def toggle(self, value: bool, clear: bool = True):
        """
        Toggle inline vision

        :param value: value of the checkbox
        :param clear: clear attachments
        """
        if not value:
            self.disable()  # disable vision
        else:
            self.enable()  # enable vision keep

        self.window.controller.ui.update_tokens()  # update tokens

    def show_inline(self):
        """Show inline vision checkbox"""
        self.window.ui.nodes['inline.vision'].setVisible(True)  # show vision checkbox

    def hide_inline(self):
        """Hide inline vision checkbox"""
        self.window.ui.nodes['inline.vision'].setVisible(False)  # hide vision checkbox

    def enable(self):
        """Enable inline vision"""
        self.is_enabled = True
        self.window.ui.nodes['inline.vision'].setChecked(True)

    def enabled(self) -> bool:
        """
        Check if inline vision is enabled

        :return: bool
        """
        return self.is_enabled

    def disable(self):
        """Disable inline vision"""
        self.is_enabled = False
        self.window.ui.nodes['inline.vision'].setChecked(False)

    def available(self):
        """Set vision content available"""
        self.is_available = True

    def unavailable(self):
        """Set vision content unavailable"""
        self.is_available = False

    def update(self):
        """Update vision content on mode change"""
        mode = self.window.core.config.get('mode')
        if mode in self.allowed_modes:
            self.show_inline()
        else:
            self.hide_inline()
