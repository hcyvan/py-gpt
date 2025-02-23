#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.01.06 06:00:00                  #
# ================================================== #

from PySide6.QtCore import QRect, QDate
from PySide6.QtGui import QColor, QBrush, QFont, Qt, QAction, QContextMenuEvent
from PySide6.QtWidgets import QCalendarWidget, QMenu

from pygpt_net.utils import trans


class CalendarSelect(QCalendarWidget):
    def __init__(self, window=None):
        """
        Calendar select widget

        :param window: main window
        """
        super(CalendarSelect, self).__init__(window)
        self.window = window
        self.currentYear = QDate.currentDate().year()
        self.currentMonth = QDate.currentDate().month()
        self.currentDay = QDate.currentDate().day()
        self.font_size = 9
        self.counters = {
            'ctx': {},  # num of ctx in date
            'notes': {},  # num of notes in date
        }
        self.setGridVisible(True)
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)  # disable num of weeks display
        self.currentPageChanged.connect(self.page_changed)
        self.clicked[QDate].connect(self.on_day_clicked)

        # context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)

    def page_changed(self, year, month):
        """
        On page changed

        :param year: Year
        :param month: Month
        """
        self.currentYear = year
        self.currentMonth = month
        self.window.controller.calendar.on_page_changed(year, month)

    def paintCell(self, painter, rect, date: QDate):
        """
        On painting cell

        :param painter: Painter
        :param rect: Rectangle
        :param date: Date
        """
        super().paintCell(painter, rect, date)
        if date in self.counters['ctx']:
            padding = 2
            task_rect = QRect(rect.right() - padding - 20, rect.top() + padding, 20, 20)
            painter.save()
            painter.setBrush(QBrush(QColor(0, 0, 0)))
            painter.drawRect(task_rect)
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont('Lato', self.font_size))
            painter.drawText(task_rect, Qt.AlignCenter, str(self.counters['ctx'][date]))
            painter.restore()

        if date in self.counters['notes']:
            day_notes = self.counters['notes'][date]
            for status, count in day_notes.items():
                padding = 2
                task_rect = QRect(rect.left() + padding, rect.bottom() - padding - 20, 20, 20)
                painter.save()
                bg_color, font_color = self.get_color_for_status(status)
                painter.setBrush(QBrush(bg_color))
                painter.drawRect(task_rect)
                painter.setPen(font_color)
                painter.setFont(QFont('Lato', self.font_size))
                painter.drawText(task_rect, Qt.AlignCenter, "!")  # str(count)
                painter.restore()

    def get_color_for_status(self, status):
        if status in self.window.controller.calendar.statuses:
            return self.window.controller.calendar.statuses[status]['color'], \
                   self.window.controller.calendar.statuses[status]['font']
        else:
            return QColor(100, 100, 100), QColor(255, 255, 255)

    def on_day_clicked(self, date: QDate):
        """
        On day clicked

        :param date: Date
        """
        year = date.year()
        month = date.month()
        day = date.day()
        self.currentYear = year
        self.currentMonth = month
        self.currentDay = day
        self.window.controller.calendar.on_day_select(year, month, day)

        # check if date has ctx TODO: think about better solution
        # if date in self.counters['ctx']:
        self.window.controller.calendar.on_ctx_select(year, month, day)

    def add_ctx(self, date: QDate, num: int):
        """
        Add ctx counter to counters list

        :param date: Date
        :param num: Number of ctx
        """
        self.counters['ctx'][date] = str(num)
        self.updateCell(date)

    def update_ctx(self, counters: dict):
        """
        Update ctx counters

        :param counters: counters dict
        """
        self.counters['ctx'] = {QDate.fromString(date_str, 'yyyy-MM-dd'): count for date_str, count in counters.items()}
        self.updateCells()

    def update_notes(self, counters: dict):
        """
        Update notes counters

        :param counters: counters dict
        """
        self.counters['notes'] = {QDate.fromString(date_str, 'yyyy-MM-dd'): count for date_str, count in counters.items()}
        self.updateCells()

    def open_context_menu(self, position):
        selected_date = self.selectedDate()
        context_menu = QMenu(self)
        action_text = trans('calendar.day.search') + ': ' + selected_date.toString()
        action = QAction(action_text, self)
        action.triggered.connect(lambda: self.execute_action(selected_date))
        context_menu.addAction(action)
        
        # set label menu
        set_label_menu = context_menu.addMenu(trans('calendar.day.label'))
        for status_id, status_info in self.window.controller.calendar.statuses.items():
            status_action = QAction(trans('calendar.day.' + status_info['label']), self)
            status_action.triggered.connect(lambda checked=False, s_id=status_id: self.set_label_for_day(selected_date, s_id))
            set_label_menu.addAction(status_action)

        context_menu.exec(self.mapToGlobal(position))

    def execute_action(self, date):
        year = date.year()
        month = date.month()
        day = date.day()
        self.window.controller.calendar.on_ctx_select(year, month, day)

    def contextMenuEvent(self, event: QContextMenuEvent):
        self.open_context_menu(event.pos())

    def set_label_for_day(self, date: QDate, status_id: int):
        self.window.controller.calendar.update_status_label(status_id, date.year(), date.month(), date.day())

