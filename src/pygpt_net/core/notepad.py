#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2023.12.31 04:00:00                  #
# ================================================== #

import datetime

from packaging.version import Version

from pygpt_net.item.notepad import NotepadItem
from pygpt_net.provider.notepad.db_sqlite import DbSqliteProvider


class Notepad:
    def __init__(self, window=None):
        """
        Notepad core

        :param window: Window instance
        """
        self.window = window
        self.provider = DbSqliteProvider(window)
        self.items = {}

    def install(self):
        """Install provider data"""
        self.provider.install()

    def patch(self, app_version: Version):
        """Patch provider data"""
        self.provider.patch(app_version)

    def get_by_id(self, idx: int) -> NotepadItem or None:
        """
        Get notepad by idx

        :param idx: notepad idx
        :return: notepad instance
        """
        if idx in self.items:
            return self.items[idx]
        return None

    def get_all(self) -> dict:
        """
        Get all notepads

        :return: notepads dict
        """
        return self.items

    def build(self) -> NotepadItem:
        """
        Build notepad

        :param idx: notepad idx
        :return: NotepadItem instance
        """
        item = NotepadItem()
        return item

    def add(self, notepad: NotepadItem) -> bool:
        """
        Add notepad

        :param notepad: NotepadItem instance
        :return: True if success
        """
        idx = self.provider.create(notepad)
        notepad.id = idx
        self.items[idx] = notepad
        self.save(idx)
        return True

    def update(self, notepad: NotepadItem) -> bool:
        """
        Update and save notepad

        :param notepad: NotepadItem instance
        :return: True if success
        """
        if notepad.idx not in self.items:
            return False

        notepad.updated_at = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        self.items[notepad.idx] = notepad
        self.save(notepad.idx)
        return True

    def load(self, idx: int):
        """
        Load notepad by idx

        :param idx: notepad idx
        """
        self.items[idx] = self.provider.load(idx)

    def load_all(self):
        """Load all notepads"""
        self.items = self.provider.load_all()

    def save(self, idx: int) -> bool:
        """
        Save notepad by idx

        :param idx: notepad idx
        :return: True if saved, False if not
        :rtype: bool
        """
        if idx not in self.items:
            return False

        self.provider.save(self.items[idx])
        return False

    def save_all(self):
        """Save all notepads"""
        self.provider.save_all(self.items)
