#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.01.02 04:00:00                  #
# ================================================== #

from pygpt_net.core.dispatcher import Event
from .editor import Editor


class Model:
    def __init__(self, window=None):
        """
        Model controller

        :param window: Window instance
        """
        self.window = window
        self.editor = Editor(window)

    def select(self, idx: int):
        """
        Select model

        :param idx: value of the list (row idx)
        """
        # check if model change is not locked
        if self.change_locked():
            return
        self.set_by_idx(self.window.core.config.get('mode'), idx)

        # update all layout
        self.window.controller.ui.update()

    def set(self, mode: str, model: str):
        """
        Set model by mode and model name

        :param mode: mode name
        :param model: model name
        """
        self.window.core.config.set('model', model)
        if 'current_model' not in self.window.core.config.data:
            self.window.core.config.data['current_model'] = {}
        self.window.core.config.data['current_model'][mode] = model

    def set_by_idx(self, mode: str, idx: int):
        """
        Set model by mode and model idx

        :param mode: mode name
        :param idx: model index
        """
        model = self.window.core.models.get_by_idx(idx, mode)
        self.window.core.config.set('model', model)
        if 'current_model' not in self.window.core.config.data:
            self.window.core.config.data['current_model'] = {}
        self.window.core.config.data['current_model'][mode] = model

        event = Event('model.select', {
            'value': model,
        })
        self.window.core.dispatcher.dispatch(event)

    def select_current(self):
        """Select current model on list"""
        mode = self.window.core.config.get('mode')
        model = self.window.core.config.get('model')
        items = self.window.core.models.get_by_mode(mode)
        if model in items:
            idx = list(items.keys()).index(model)
            current = self.window.ui.models['prompt.model'].index(idx, 0)
            self.window.ui.nodes['prompt.model'].setCurrentIndex(current)

    def select_default(self):
        """Set default model"""
        model = self.window.core.config.get('model')
        if model is None or model == "":
            mode = self.window.core.config.get('mode')

            # set previous selected model
            current_models = self.window.core.config.get('current_model')
            if mode in current_models and \
                    current_models[mode] is not None and \
                    current_models[mode] != "" and \
                    current_models[mode] in self.window.core.models.get_by_mode(mode):
                self.window.core.config.set('model', current_models[mode])
            else:
                # or set default model
                self.window.core.config.set('model', self.window.core.models.get_default(mode))

    def update_list(self):
        """Update models list"""
        mode = self.window.core.config.get('mode')
        self.window.ui.toolbox.model.update(self.window.core.models.get_by_mode(mode))

    def update(self):
        """Update models"""
        self.select_default()
        self.update_list()
        self.select_current()

    def change_locked(self) -> bool:
        """
        Check if model change is locked

        :return: True if locked
        """
        return self.window.controller.chat.input.generating
