#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.01.04 06:00:00                  #
# ================================================== #

from datetime import datetime

from pygpt_net.plugin.base import BasePlugin
from pygpt_net.core.dispatcher import Event


class Plugin(BasePlugin):
    def __init__(self, *args, **kwargs):
        super(Plugin, self).__init__(*args, **kwargs)
        self.id = "real_time"
        self.name = "Real Time"
        self.description = "Appends current time and date to every system prompt."
        self.order = 2
        self.use_locale = True
        self.init_options()

    def init_options(self):
        """
        Initialize options
        """
        self.add_option("hour", "bool", True,
                        "Append time",
                        "If enabled, current time will be appended to system prompt.",
                        tooltip="Hour will be appended to system prompt.")
        self.add_option("date", "bool", True,
                        "Append date",
                        "If enabled, current date will be appended to system prompt.",
                        tooltip="Date will be appended to system prompt.")

        desc = "Template to append to system prompt.\nPlaceholder {time} will be replaced with current date and time " \
               "in real-time. "
        tooltip = "Text to append to system prompt."
        self.add_option("tpl", "textarea", " Current time is {time}.",
                        "Template", desc, tooltip=tooltip)

    def setup(self) -> dict:
        """
        Return available config options

        :return: config options
        """
        return self.options

    def attach(self, window):
        """
        Attach window

        :param window: Window instance
        """
        self.window = window

    def handle(self, event: Event, *args, **kwargs):
        """
        Handle dispatched event

        :param event: event object
        """
        name = event.name
        data = event.data

        if name == 'system.prompt':
            silent = False
            if 'silent' in data and data['silent']:
                silent = True
            data['value'] = self.on_system_prompt(data['value'], silent)

    def on_system_prompt(self, prompt: str, silent: bool = False):
        """
        Event: On prepare system prompt

        :param prompt: prompt
        :param silent: silent mode
        :return: updated prompt
        :rtype: str
        """
        if not silent:
            self.debug("Plugin: real_time:on_system_prompt [before]: " + str(prompt))  # log

        if self.get_option_value("hour") or self.get_option_value("date"):
            if self.get_option_value("hour") and self.get_option_value("date"):
                prompt += self.get_option_value("tpl").format(time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            elif self.get_option_value("hour"):
                prompt += self.get_option_value("tpl").format(time=datetime.now().strftime('%H:%M:%S'))
            elif self.get_option_value("date"):
                prompt += self.get_option_value("tpl").format(time=datetime.now().strftime('%Y-%m-%d'))

        if not silent:
            self.debug("Plugin: real_time:on_system_prompt [after]: " + str(prompt))  # log
        return prompt
