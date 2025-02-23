#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.01.07 02:00:00                  #
# ================================================== #

from PySide6.QtGui import QAction

from pygpt_net.controller.plugins.settings import Settings
from pygpt_net.core.dispatcher import Event
from pygpt_net.item.ctx import CtxItem
from pygpt_net.utils import trans


class Plugins:
    def __init__(self, window=None):
        """
        Plugins controller

        :param window: Window instance
        """
        self.window = window
        self.settings = Settings(window)
        self.enabled = {}

    def setup(self):
        """Set up plugins"""
        self.setup_menu()
        self.setup_ui()
        self.setup_config()
        self.update()

    def setup_ui(self):
        """Set up plugins UI"""
        for id in self.window.core.plugins.get_ids():
            try:
                # setup UI
                self.window.core.plugins.get(id).setup_ui()
            except AttributeError:
                pass

        # show/hide UI elements
        self.handle_types()

        # tmp dump locales
        # self.window.core.plugins.dump_locales()

    def setup_menu(self):
        """Set up plugins menu"""
        for id in self.window.core.plugins.get_ids():
            plugin = self.window.core.plugins.get(id)
            if id in self.window.ui.menu['plugins']:
                continue
            default_name = plugin.name
            trans_key = 'plugin.' + id
            name = trans(trans_key)
            if name == trans_key:
                name = default_name
            if plugin.use_locale:
                domain = 'plugin.{}'.format(id)
                name = trans('plugin.name', False, domain)
            self.window.ui.menu['plugins'][id] = QAction(name, self.window, checkable=True)
            self.window.ui.menu['plugins'][id].triggered.connect(
                lambda checked=None, id=id: self.toggle(id))
            self.window.ui.menu['menu.plugins'].addAction(self.window.ui.menu['plugins'][id])

    def setup_config(self):
        """Enable plugins from config"""
        for id in self.window.core.config.get('plugins_enabled'):
            if self.window.core.config.data['plugins_enabled'][id]:
                self.enable(id)

    def update(self):
        """Update plugins menu"""
        for id in self.window.ui.menu['plugins']:
            self.window.ui.menu['plugins'][id].setChecked(False)

        for id in self.enabled:
            if self.enabled[id]:
                self.window.ui.menu['plugins'][id].setChecked(True)

        self.handle_types()
        self.window.controller.ui.update_active()  # refresh active elements
        self.window.controller.ui.update_vision()  # vision camera

    def enable(self, id: str):
        """
        Enable plugin

        :param id: plugin id
        """
        if self.window.core.plugins.is_registered(id):
            self.enabled[id] = True
            self.window.core.plugins.enable(id)

            # dispatch event
            event = Event('enable', {
                'value': id,
            })
            self.window.core.dispatcher.dispatch(event)

            # update audio menu
            if self.has_type(id, 'audio.input') or self.has_type(id, 'audio.output'):
                self.window.controller.audio.update()

        self.update_info()
        self.update()

    def disable(self, id: str):
        """
        Disable plugin

        :param id: plugin id
        """
        if self.window.core.plugins.is_registered(id):
            self.enabled[id] = False
            self.window.core.plugins.disable(id)

            # dispatch event
            event = Event('disable', {
                'value': id,
            })
            self.window.core.dispatcher.dispatch(event)

            # update audio menu
            if self.has_type(id, 'audio.input') or self.has_type(id, 'audio.output'):
                self.window.controller.audio.update()

        self.update_info()
        self.update()

    def is_enabled(self, id: str):
        """
        Check if plugin is enabled

        :param id: plugin id
        :return: True if enabled
        :rtype: bool
        """
        if self.window.core.plugins.is_registered(id):
            if id in self.enabled:
                return self.enabled[id]
        return False

    def toggle(self, id: str):
        """
        Toggle plugin

        :param id: plugin id
        """
        if self.window.core.plugins.is_registered(id):
            if self.is_enabled(id):
                self.disable(id)
            else:
                self.enable(id)

        self.handle_types()
        self.window.controller.ui.update_tokens()  # refresh tokens
        self.window.controller.ui.update_active()  # refresh active elements
        self.window.controller.ui.update_vision()  # vision camera
        self.window.controller.attachment.update()  # attachments update

    def set_by_tab(self, idx: int):
        """
        Set current plugin by tab index

        :param idx: tab index
        """
        plugin_idx = 0
        for id in self.window.core.plugins.get_ids():
            if self.window.core.plugins.has_options(id):
                if plugin_idx == idx:
                    self.settings.current_plugin = id
                    break
                plugin_idx += 1
        current = self.window.ui.models['plugin.list'].index(idx, 0)
        self.window.ui.nodes['plugin.list'].setCurrentIndex(current)

    def get_tab_idx(self, plugin_id: str) -> int:
        """
        Get plugin tab index

        :param plugin_id: plugin id
        :return: tab index
        """
        plugin_idx = None
        i = 0
        for id in self.window.core.plugins.get_ids():
            if id == plugin_id:
                plugin_idx = i
                break
            i += 1
        return plugin_idx

    def unregister(self, id: str):
        """
        Unregister plugin

        :param id: plugin id
        """
        self.window.core.plugins.unregister(id)
        if id in self.enabled:
            self.enabled.pop(id)

    def destroy(self):
        """Destroy plugins workers"""

        # send force stop event
        event = Event('force.stop', {})
        self.window.core.dispatcher.dispatch(event)

        for id in self.window.core.plugins.get_ids():
            try:
                # destroy plugin workers
                self.window.core.plugins.destroy(id)
            except AttributeError:
                pass

    def has_type(self, id: str, type: str):
        """
        Check if plugin has type
        :param id: plugin ID
        :param type: type to check
        :return: True if has type
        """
        if self.window.core.plugins.is_registered(id):
            if type in self.window.core.plugins.get(id).type:
                return True
        return False

    def is_type_enabled(self, type: str) -> bool:
        """
        Check if plugin type is enabled

        :param type: plugin type
        :return: True if enabled
        """
        enabled = False
        for id in self.window.core.plugins.get_ids():
            if type in self.window.core.plugins.get(id).type and self.is_enabled(id):
                enabled = True
                break
        return enabled

    def handle_types(self):
        """Handle plugin type"""
        for type in self.window.core.plugins.allowed_types:
            if type == 'audio.input':
                if self.is_type_enabled(type):
                    self.window.ui.plugin_addon['audio.input'].setVisible(True)
                else:
                    self.window.ui.plugin_addon['audio.input'].setVisible(False)
            elif type == 'audio.output':
                if self.is_type_enabled(type):
                    pass
                    # self.window.ui.plugin_addon['audio.output'].setVisible(True)
                else:
                    self.window.ui.plugin_addon['audio.output'].setVisible(False)
            elif type == 'schedule':
                if self.is_type_enabled(type):
                    self.window.ui.plugin_addon['schedule'].setVisible(True)
                else:
                    self.window.ui.plugin_addon['schedule'].setVisible(False)

    def on_update(self):
        """Called on update"""
        for id in self.window.core.plugins.get_ids():
            if self.is_enabled(id):
                try:
                    self.window.core.plugins.get(id).on_update()
                except AttributeError:
                    pass

    def on_post_update(self):
        """Called on post update"""
        for id in self.window.core.plugins.get_ids():
            if self.is_enabled(id):
                try:
                    self.window.core.plugins.get(id).on_post_update()
                except AttributeError:
                    pass

    def update_info(self):
        """Update plugins info"""
        enabled_list = []
        for id in self.window.core.plugins.get_ids():
            if self.is_enabled(id):
                enabled_list.append(self.window.core.plugins.get(id).name)
        tooltip = " + ".join(enabled_list)

        count_str = ""
        c = 0
        if len(self.window.core.plugins.get_ids()) > 0:
            for id in self.window.core.plugins.get_ids():
                if self.is_enabled(id):
                    c += 1

        if c > 0:
            count_str = "+ " + str(c) + " " + trans('chatbox.plugins')
        self.window.ui.nodes['chat.plugins'].setText(count_str)
        self.window.ui.nodes['chat.plugins'].setToolTip(tooltip)  

    def apply_cmds(self, ctx: CtxItem, cmds: list):
        """
        Apply commands

        :param ctx: CtxItem
        :param cmds: commands
        """
        commands = []
        for cmd in cmds:
            if 'cmd' in cmd:
                commands.append(cmd)

        if len(commands) == 0:
            return

        # dispatch 'cmd.execute' event
        event = Event('cmd.execute', {
            'commands': commands
        })
        event.ctx = ctx
        self.window.controller.command.dispatch(event)

    def apply_cmds_only(self, ctx: CtxItem, cmds: list):
        """
        Apply commands

        :param ctx: CtxItem
        :param cmds: commands
        """
        commands = []
        for cmd in cmds:
            if 'cmd' in cmd:
                commands.append(cmd)

        if len(commands) == 0:
            return

        # dispatch 'cmd.only' event
        event = Event('cmd.only', {
            'commands': commands
        })
        event.ctx = ctx
        self.window.controller.command.dispatch(event)
