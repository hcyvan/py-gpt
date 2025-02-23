#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.01.08 17:00:00                  #
# ================================================== #

from pygpt_net.core.dispatcher import Event
from pygpt_net.utils import trans


class Mode:
    def __init__(self, window=None):
        """
        Mode controller

        :param window: Window instance
        """
        self.window = window

    def select(self, idx: int):
        """
        Select mode by idx

        :param idx: value of the list (row idx)
        """
        # check if mode change is not locked
        if self.change_locked():
            return
        mode = self.window.core.modes.get_by_idx(idx)
        self.set(mode)

        event = Event('mode.select', {
            'value': mode,
        })
        self.window.core.dispatcher.dispatch(event)

    def set(self, mode: str):
        """
        Set mode

        :param mode: mode name
        """
        # if ctx loaded with assistant then switch to this assistant
        if mode == "assistant":
            if self.window.core.ctx.current is not None \
                    and self.window.core.ctx.assistant is not None:
                self.window.controller.assistant.select_by_id(self.window.core.ctx.assistant)

        self.window.core.config.set('mode', mode)
        self.window.core.config.set('model', "")
        self.window.core.config.set('preset', "")

        # update
        self.window.controller.attachment.update()
        self.window.controller.ctx.update_ctx()
        self.window.controller.ui.update()
        self.window.ui.status(trans('status.started'))

        # vision camera
        self.window.controller.ui.update_vision()

        # if assistant mode then update ctx label
        if mode == "assistant":
            self.window.controller.ctx.common.update_label_by_current()

    def select_current(self):
        """Select current on the list"""
        mode = self.window.core.config.get('mode')
        idx = self.window.core.modes.get_idx_by_name(mode)
        current = self.window.ui.models['prompt.mode'].index(idx, 0)
        self.window.ui.nodes['prompt.mode'].setCurrentIndex(current)

    def select_default(self):
        """Set default mode"""
        mode = self.window.core.config.get('mode')
        if mode is None or mode == "":
            self.window.core.config.set('mode', self.window.core.modes.get_default())

    def default_all(self):
        """Set default mode, model and preset"""
        self.select_default()
        self.window.controller.model.select_default()
        self.window.controller.presets.select_default()
        self.window.controller.assistant.select_default()

    def update_list(self):
        """Update modes list"""
        self.window.ui.toolbox.mode.update(self.window.core.modes.get_all())

    def update_temperature(self, temperature: float = None):
        """
        Update current temperature field

        :param temperature: current temperature
        :type temperature: float or None
        """
        if temperature is None:
            if self.window.core.config.get('preset') is None or self.window.core.config.get('preset') == "":
                temperature = 1.0  # default temperature
            else:
                id = self.window.core.config.get('preset')
                if id in self.window.core.presets.items:
                    temperature = float(self.window.core.presets.items[id].temperature or 1.0)
        option = self.window.controller.settings.editor.get_options()["temperature"]
        '''
        self.window.controller.config.slider.on_update("global", "current_temperature", option, temperature,
                                                       hooks=False)  # disable hooks to prevent circular update
        '''

    def hook_global_temperature(self, key, value, caller, *args, **kwargs):
        """
        Hook: on update current temperature global field
        """
        if caller != "slider":
            return  # accept call only from slider (has already validated min/max)

        temperature = value / 100
        self.window.core.config.set("temperature", temperature)
        preset_id = self.window.core.config.get('preset')
        if preset_id is not None and preset_id != "":
            if preset_id in self.window.core.presets.items:
                preset = self.window.core.presets.items[preset_id]
                preset.temperature = temperature
                self.window.core.presets.save(preset_id)

    def update_mode(self):
        """Update mode"""
        self.select_default()
        self.update_list()
        self.select_current()
        self.window.controller.chat.vision.update()

    def reset_current(self):
        """Reset current setup"""
        self.window.core.config.set('prompt', None)
        self.window.core.config.set('ai_name', None)
        self.window.core.config.set('user_name', None)

    def change_locked(self) -> bool:
        """
        Check if mode change is locked

        :return: True if locked
        :rtype: bool
        """
        return self.window.controller.chat.input.generating
