#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.01.06 23:00:00                  #
# ================================================== #

from pygpt_net.plugin.base import BasePlugin
from pygpt_net.core.dispatcher import Event
from pygpt_net.item.ctx import CtxItem

from .websearch import WebSearch
from .worker import Worker


class Plugin(BasePlugin):
    def __init__(self, *args, **kwargs):
        super(Plugin, self).__init__(*args, **kwargs)
        self.id = "cmd_web_google"
        self.name = "Command: Google Web Search"
        self.description = "Allows to connect to the Web and search web pages for actual data."
        self.urls = {}
        self.input_text = None
        self.allowed_cmds = ["web_search", "web_url_open"]
        self.order = 100
        self.use_locale = True
        self.init_options()
        self.websearch = WebSearch(self)

    def init_options(self):
        """Initialize options"""
        url_api = {
            "API Key": "https://developers.google.com/custom-search/v1/overview",
        }
        url_cx = {
            "CX ID": "https://programmablesearchengine.google.com/controlpanel/all",
        }
        self.add_option("google_api_key", "text", "",
                        "Google Custom Search API KEY",
                        "You can obtain your own API key at https://developers.google.com/custom-search/v1/overview",
                        tooltip="Google Custom Search CX ID", secret=True, persist=True, urls=url_api)
        self.add_option("google_api_cx", "text", "",
                        "Google Custom Search CX ID",
                        "You will find your CX ID at https://programmablesearchengine.google.com/controlpanel/all"
                        "\nRemember to enable \"Search on ALL internet pages\" option in project settings.",
                        tooltip="Google Custom Search CX ID", secret=True, persist=True, urls=url_cx)
        self.add_option("num_pages", "int", 10,
                        "Number of pages to search",
                        "Number of max pages to search per query",
                        min=1, max=None)
        self.add_option("max_page_content_length", "int", 0,
                        "Max content characters",
                        "Max characters of page content to get (0 = unlimited)",
                        min=0, max=None)
        self.add_option("chunk_size", "int", 100000,
                        "Per-page content chunk size",
                        "Per-page content chunk size (max characters per chunk)",
                        min=1, max=None)
        self.add_option("use_google", "bool", True,
                        "Use Google Custom Search",
                        "Enable Google Custom Search API (API key required)",
                        tooltip="Google Custom Search")
        """
        self.add_option("use_wikipedia", "bool", True,
                        "Use Wikipedia",
                        "Enable above option to use Wikipedia API (free, no API key required)",
                        tooltip="Wikipedia API")
        """
        self.add_option("disable_ssl", "bool", True,
                        "Disable SSL verify",
                        "Disables SSL verification when crawling web pages",
                        tooltip="Disable SSL verify")
        self.add_option("max_result_length", "int", 1500,
                        "Max result length",
                        "Max length of summarized result (characters)",
                        min=0, max=None)
        self.add_option("summary_max_tokens", "int", 1500,
                        "Max summary tokens",
                        "Max tokens in output when generating summary",
                        min=0, max=None)
        self.add_option("summary_model", "text", "gpt-3.5-turbo-1106",
                        "Model used for web page summarize",
                        "Model used for web page summarize, default: gpt-3.5-turbo-1106", advanced=True)
        self.add_option("prompt_summarize", "textarea", "Summarize text in English in a maximum of 3 paragraphs, "
                                                        "trying to find the most important content that can help "
                                                        "answer the following question: {query}",
                        "Summarize prompt",
                        "Prompt used for web search results summarize, use {query} as a placeholder for search query",
                        tooltip="Prompt", advanced=True)
        self.add_option("prompt_summarize_url", "textarea", "Summarize text in English in a maximum of 3 paragraphs, "
                                                            "trying to find the most important content.",
                        "Summarize prompt (URL open)",
                        "Prompt used for specified URL page summarize",
                        tooltip="Prompt", advanced=True)

        self.add_option("syntax_web_search", "textarea", '"web_search": use it to search the Web for more info, '
                                                         'prepare a query for the search engine itself, start from '
                                                         'page 1. If you don\'t find anything or don\'t find enough '
                                                         'information, try the next page. Use a custom summary prompt '
                                                         'if necessary, otherwise, a default summary will be used. '
                                                         'Max pages limit: {max_pages}, params: "query", "page", '
                                                         '"summarize_prompt"',
                        "Syntax: web_search",
                        "Syntax for web search command, use {max_pages} as a placeholder for `num_pages` value",
                        advanced=True)
        self.add_option("syntax_web_url_open", "textarea", '"web_url_open": use it to get contents from a specific '
                                                           'Web page. Use a custom summary prompt if necessary, '
                                                           'otherwise a default summary will be used. Params: "url", '
                                                           '"summarize_prompt"',
                        "Syntax: web_url_open",
                        "Syntax for web URL open command", advanced=True)

    def setup(self) -> dict:
        """
        Return available config options

        :return: config options
        """
        return self.options

    def attach(self, window):
        """
        Attach window

        :param window: Window
        """
        self.window = window

    def handle(self, event: Event, *args, **kwargs):
        """
        Handle dispatched event

        :param event: event object
        """
        name = event.name
        data = event.data
        ctx = event.ctx

        if name == 'input.before':
            self.on_input_before(data['value'])
        elif name == 'cmd.syntax':
            self.cmd_syntax(data)
        elif name == 'cmd.execute':
            self.cmd(ctx, data['commands'])

    def on_input_before(self, text: str):
        """
        Event: Before input

        :param text: text
        """
        self.input_text = text

    def log(self, msg: str):
        """
        Log message to console

        :param msg: message to log
        """
        full_msg = '[CMD] ' + str(msg)
        self.debug(full_msg)
        self.window.ui.status(full_msg)
        print(full_msg)

    def cmd_syntax(self, data: dict):
        """
        Event: On cmd syntax prepare

        :param data: event data dict
        """
        for option in self.allowed_cmds:
            key = "syntax_" + option
            if self.has_option(key):
                data['syntax'].append(self.get_option_value(key))

    def cmd(self, ctx: CtxItem, cmds: list):
        """
        Event: On cmd

        :param ctx: CtxItem
        :param cmds: commands dict
        """
        is_cmd = False
        need_api_key = False
        my_commands = []
        for item in cmds:
            if item["cmd"] in self.allowed_cmds:
                my_commands.append(item)
                is_cmd = True
                if item["cmd"] == "web_search":
                    need_api_key = True

        if not is_cmd:
            return

        # check API key
        key = self.get_option_value("google_api_key")
        cx = self.get_option_value("google_api_cx")
        if need_api_key and (key is None or cx is None or key == "" or cx == ""):
            self.gen_api_key_response(ctx, cmds)
            self.window.ui.dialogs.alert("Google API key and CX ID are required for this command to work. "
                                         "Please go to the plugin settings and enter your API key and CX ID.")
            return

        try:
            # worker
            worker = Worker()
            worker.plugin = self
            worker.cmds = my_commands
            worker.ctx = ctx
            worker.websearch = self.websearch

            # signals (base handlers)
            worker.signals.finished.connect(self.handle_finished)
            worker.signals.log.connect(self.handle_log)
            worker.signals.debug.connect(self.handle_debug)
            worker.signals.status.connect(self.handle_status)
            worker.signals.error.connect(self.handle_error)

            # INTERNAL MODE (sync)
            # if internal (autonomous) call then use synchronous call
            if ctx.internal:
                worker.run()
                return

            # start
            self.window.threadpool.start(worker)

        except Exception as e:
            self.error(e)

    def gen_api_key_response(self, ctx: CtxItem, cmds: list):
        """
        Generate response for empty API key error

        :param ctx: CtxItem
        :param cmds: commands dict
        """
        for item in cmds:
            request = {"cmd": item["cmd"]}
            err = "Google API key or CX is not set. Please set credentials in plugin settings."
            self.log(err)
            self.window.ui.status(err)
            msg = "Tell the user that the Google API key is not configured in the plugin settings, " \
                  "and to set the API key in the settings in order to use the internet search plugin."
            data = {
                'msg_to_user': msg,
            }
            response = {"request": request, "result": data}
            ctx.results.append(response)
            ctx.reply = True
            return
