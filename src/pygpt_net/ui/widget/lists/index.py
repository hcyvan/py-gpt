#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.01.16 06:00:00                  #
# ================================================== #

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu

from pygpt_net.ui.widget.lists.base import BaseList
from pygpt_net.utils import trans


class IndexList(BaseList):
    def __init__(self, window=None, id=None):
        """
        Index select menu

        :param window: main window
        :param id: input id
        """
        super(IndexList, self).__init__(window)
        self.window = window
        self.id = id

    def click(self, val):
        self.window.controller.idx.select(val.row())

    def contextMenuEvent(self, event):
        """
        Context menu event

        :param event: context menu event
        """
        actions = {}
        actions['edit'] = QAction(QIcon.fromTheme("edit-edit"), trans('action.edit'), self)
        actions['edit'].triggered.connect(
            lambda: self.action_edit(event))

        txt = trans('idx.index_now') + ': ' + trans('settings.llama.extra.btn.idx_db_all')
        actions['idx_db_all'] = QAction(QIcon.fromTheme("search"), txt, self)
        actions['idx_db_all'].triggered.connect(
            lambda: self.action_idx_db_all(event))

        txt = trans('idx.index_now') + ': ' + trans('settings.llama.extra.btn.idx_db_update')
        actions['idx_db_update'] = QAction(QIcon.fromTheme("search"), txt, self)
        actions['idx_db_update'].triggered.connect(
            lambda: self.action_idx_db_update(event))

        txt = trans('idx.index_now') + ': ' + trans('settings.llama.extra.btn.idx_files_all')
        actions['idx_files_all'] = QAction(QIcon.fromTheme("search"), txt, self)
        actions['idx_files_all'].triggered.connect(
            lambda: self.action_idx_files_all(event))

        actions['delete'] = QAction(QIcon.fromTheme("edit-delete"), trans('idx.btn.clear'), self)
        actions['delete'].triggered.connect(
            lambda: self.action_clear(event))

        menu = QMenu(self)
        menu.addAction(actions['edit'])
        menu.addAction(actions['idx_db_all'])
        menu.addAction(actions['idx_db_update'])
        menu.addAction(actions['idx_files_all'])
        menu.addAction(actions['delete'])

        item = self.indexAt(event.pos())
        idx = item.row()
        if idx >= 0:
            self.window.controller.idx.select(item.row())
            menu.exec_(event.globalPos())

    def action_idx_db_all(self, event):
        """
        Idx action handler

        :param event: mouse event
        """
        item = self.indexAt(event.pos())
        idx = item.row()
        if idx >= 0:
            self.window.controller.idx.idx_db_all_by_idx(idx)

    def action_idx_db_update(self, event):
        """
        Idx action handler

        :param event: mouse event
        """
        item = self.indexAt(event.pos())
        idx = item.row()
        if idx >= 0:
            self.window.controller.idx.idx_db_update_by_idx(idx)

    def action_idx_files_all(self, event):
        """
        Idx action handler

        :param event: mouse event
        """
        item = self.indexAt(event.pos())
        idx = item.row()
        if idx >= 0:
            self.window.controller.idx.idx_files_all_by_idx(idx)

    def action_edit(self, event):
        """
        Edit action handler

        :param event: mouse event
        """
        item = self.indexAt(event.pos())
        idx = item.row()
        if idx >= 0:
            self.window.controller.settings.open_section('llama-index')

    def action_clear(self, event):
        """
        Clear idx action handler

        :param event: mouse event
        """
        item = self.indexAt(event.pos())
        idx = item.row()
        if idx >= 0:
            self.window.controller.idx.indexer.clear_by_idx(idx)
