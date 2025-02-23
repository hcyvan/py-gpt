#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.01.09 02:00:00                  #
# ================================================== #

from pygpt_net.plugin.base import BasePlugin
from pygpt_net.core.dispatcher import Event

from datetime import datetime
from croniter import croniter


class Plugin(BasePlugin):
    def __init__(self, *args, **kwargs):
        super(Plugin, self).__init__(*args, **kwargs)
        self.id = "crontab"
        self.name = "Crontab / Task scheduler"
        self.type = ['schedule']
        self.description = "Plugin provides cron-based job scheduling - " \
                           "you can schedule prompts to be sent at any time using cron-based syntax for task setup."
        self.order = 100
        self.use_locale = True
        self.timers = []
        self.init_options()

    def init_options(self):
        """Initialize options"""
        keys = {
            "enabled": "bool",
            "crontab": "text",
            "prompt": "textarea",
            "preset": {
                "type": "combo",
                "use": "presets",
                "keys": []
            },
        }
        value = [
            {
                "enabled": False,
                "crontab": "30 9 * * *",
                "prompt": "Hi! This prompt should be sent at 9:30 every day. What time is it?",
                "preset": "_",
            },
        ]
        desc = "Add your cron-style tasks here. They will be executed automatically at the times you specify in " \
               "the cron-based job format. If you are unfamiliar with Cron, consider visiting the Cron Guru " \
               "page for assistance."
        tooltip = "Check out the tutorials about Cron or visit the Crontab Guru for help on how to use Cron syntax."
        self.add_option("crontab", "dict", value,
                        "Your tasks", desc, tooltip, keys=keys, urls={"Crontab Guru": "https://crontab.guru"})
        self.add_option("new_ctx", "bool", True,
                        "Create a new context on job run",
                        "If enabled, then a new context will be created on every run of the job")

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

    def on_update(self):
        pass

    def on_post_update(self):
        """
        On post update hook
        """
        self.schedule_tasks()

    def handle(self, event: Event, *args, **kwargs):
        """
        Handle dispatched event

        :param event: event object
        """
        pass

    def job(self, item):
        """
        Execute task

        :param item: task item
        """
        if item["prompt"] == "" or item["prompt"] is None:
            self.log("Prompt is empty, skipping task")
            return

        self.log("Executing task: {}: {}".format(datetime.now(), item["prompt"]))

        # select preset if defined and exists
        if item["preset"] != "_" and item["preset"] is not None:
            if self.window.core.presets.exists(item["preset"]):
                mode = self.window.core.presets.get_first_mode(item["preset"])
                if mode is not None:
                    self.log("Using preset: {}".format(item["preset"]))
                    self.window.controller.presets.set(mode, item["preset"])
                    self.window.controller.presets.select_current()
                    self.window.controller.presets.select_model()

        # send prompt
        if self.get_option_value("new_ctx"):
            self.window.controller.ctx.new(force=True)
        self.window.controller.chat.input.send(item["prompt"], force=True)

    def schedule_tasks(self):
        """Schedule tasks based on crontab"""
        crontab = self.get_option_value("crontab")
        # remove unused or inactive items
        for timer in self.timers:
            if not timer["item"]["enabled"] or timer["item"] not in crontab:
                self.timers.remove(timer)

        for item in crontab:
            try:
                if not item["enabled"]:
                    continue
                cron = item["crontab"]
                base_time = datetime.now()
                iter = croniter(cron, base_time)

                is_timer = False
                timer = None
                for timer in self.timers:
                    if item == timer["item"]:
                        is_timer = True
                        break

                # add to timers if not exists
                if not is_timer:
                    timer = {"item": item, "next_time": None}
                    self.timers.append(timer)

                next_time = timer["next_time"]

                # if first run
                if next_time is None:
                    next_time = iter.get_next(datetime)
                    timer["next_time"] = next_time
                    continue

                if datetime.now() >= next_time:
                    next_time = iter.get_next(datetime)
                    timer["next_time"] = next_time
                    self.job(item)

                timer["next_time"] = iter.get_next(datetime)
            except Exception as e:
                self.log("Error: {}".format(e))

        # show number of scheduled jobs
        num_jobs = len(self.timers)
        if num_jobs > 0:
            self.window.ui.plugin_addon['schedule'].setVisible(True)
            self.window.ui.plugin_addon['schedule'].setText("+ Cron: {} job(s)".format(len(self.timers)))
        else:
            self.window.ui.plugin_addon['schedule'].setVisible(False)
            self.window.ui.plugin_addon['schedule'].setText("")

    def log(self, msg: str):
        """
        Log message to console

        :param msg: message to log
        """
        full_msg = '[CRON] ' + str(msg)
        self.debug(full_msg)
        self.window.ui.status(full_msg)
        print(full_msg)
