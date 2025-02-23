#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.01.15 05:00:00                  #
# ================================================== #

from PySide6 import QtCore
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QVBoxLayout, QLabel, QWidget

from pygpt_net.ui.widget.lists.model import ModelList
from pygpt_net.utils import trans


class Model:
    def __init__(self, window=None):
        """
        Toolbox UI

        :param window: Window instance
        """
        self.window = window
        self.id = 'prompt.model'

    def setup(self) -> QWidget:
        """
        Setup models

        :return: QWidget7
        """
        widget = QWidget()
        widget.setLayout(self.setup_list())

        return widget

    def setup_list(self) -> QVBoxLayout:
        """
        Setup list

        :return: QVBoxLayout
        """
        label_key = self.id + '.label'

        self.window.ui.nodes[label_key] = QLabel(trans("toolbox.model.label"))
        self.window.ui.nodes[label_key].setStyleSheet(self.window.controller.theme.style('text_bold'))
        self.window.ui.nodes[self.id] = ModelList(self.window, self.id)
        self.window.ui.nodes[self.id].selection_locked = self.window.controller.model.change_locked

        layout = QVBoxLayout()
        layout.addWidget(self.window.ui.nodes[label_key])
        layout.addWidget(self.window.ui.nodes[self.id])

        self.window.ui.models[self.id] = self.create_model(self.window)
        self.window.ui.nodes[self.id].setModel(self.window.ui.models[self.id])

        # prevent focus out selection leave
        self.window.ui.nodes[self.id].selectionModel().selectionChanged.connect(
            self.window.ui.nodes[self.id].lockSelection)

        return layout

    def create_model(self, parent) -> QStandardItemModel:
        """
        Create list model

        :param parent: parent widget
        :return: QStandardItemModel
        """
        return QStandardItemModel(0, 1, parent)

    def update(self, data):
        """
        Update list

        :param data: Data to update
        """
        # store previous selection
        self.window.ui.nodes[self.id].backup_selection()

        self.window.ui.models[self.id].removeRows(0, self.window.ui.models[self.id].rowCount())
        i = 0
        for n in data:
            self.window.ui.models[self.id].insertRow(i)
            name = data[n].name
            index = self.window.ui.models[self.id].index(i, 0)
            self.window.ui.models[self.id].setData(index, data[n].id, QtCore.Qt.ToolTipRole)
            self.window.ui.models[self.id].setData(self.window.ui.models[self.id].index(i, 0), name)
            i += 1

        # restore previous selection
        self.window.ui.nodes[self.id].restore_selection()
