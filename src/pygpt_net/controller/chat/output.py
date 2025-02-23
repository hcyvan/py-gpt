#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.01.14 09:00:00                  #
# ================================================== #

from PySide6.QtWidgets import QApplication

from pygpt_net.core.dispatcher import Event
from pygpt_net.item.ctx import CtxItem
from pygpt_net.utils import trans


class Output:
    def __init__(self, window=None):
        """
        Output controller

        :param window: Window instance
        """
        self.window = window
        self.not_stream_modes = ['assistant', 'img']

    def handle(self, ctx: CtxItem, mode: str, stream_mode: bool = False):
        """
        Handle response from LLM

        :param ctx: CtxItem
        :param mode: mode
        :param stream_mode: async stream mode
        """
        # if stream mode then append chunk by chunk
        if stream_mode and mode not in self.not_stream_modes:
            self.append_stream(ctx, mode)

        # event: ctx.after
        event = Event('ctx.after')
        event.ctx = ctx
        self.window.core.dispatcher.dispatch(event)

        # log
        self.log("Context: output [after plugin: ctx.after]: {}".format(self.window.core.ctx.dump(ctx)))
        self.log("Appending output to chat window...")

        # only append output if not in async stream mode, TODO: plugin output add
        if not stream_mode:
            self.window.controller.chat.render.append_output(ctx)
            self.window.controller.chat.render.append_extra(ctx)

        self.handle_complete(ctx)

    def append_stream(self, ctx: CtxItem, mode: str):
        """
        Handle stream response from LLM

        :param ctx: CtxItem
        :param mode: mode
        """
        output = ""
        output_tokens = 0
        begin = True
        sub_mode = None  # sub mode for langchain (chat, completion)

        # get sub mode for langchain
        if mode == "langchain":
            model_config = self.window.core.models.get(self.window.core.config.get('model'))
            sub_mode = 'chat'
            # get available modes for langchain
            if 'mode' in model_config.langchain:
                if 'chat' in model_config.langchain['mode']:
                    sub_mode = 'chat'
                elif 'completion' in model_config.langchain['mode']:
                    sub_mode = 'completion'

        # chunks: stream begin
        self.window.controller.chat.render.stream_begin()

        # read stream
        try:
            if ctx.stream is not None:
                self.log("Reading stream...")  # log
                for chunk in ctx.stream:
                    # if force stop then break
                    if self.window.controller.chat.input.stop:
                        break

                    response = None

                    # chat and vision
                    if mode == "chat" or mode == "vision":
                        if chunk.choices[0].delta.content is not None:
                            response = chunk.choices[0].delta.content

                    # completion
                    elif mode == "completion":
                        if chunk.choices[0].text is not None:
                            response = chunk.choices[0].text

                    # llama_index
                    elif mode == "llama_index":
                        if chunk is not None:
                            response = chunk

                    # langchain (can provide different modes itself)
                    elif mode == "langchain":
                        if sub_mode == 'chat':
                            # if chat model response is an object
                            if chunk.content is not None:
                                response = chunk.content
                        elif sub_mode == 'completion':
                            # if completion response is string
                            if chunk is not None:
                                response = chunk

                    if response is not None:
                        if begin and response == "":  # prevent empty beginning
                            continue
                        output += response
                        output_tokens += 1
                        self.window.controller.chat.render.append_chunk(ctx, response, begin)
                        self.window.controller.ui.update_tokens()  # update UI
                        QApplication.processEvents()  # process events to update UI after each chunk
                        begin = False

        except Exception as e:
            self.window.core.debug.log(e)

        # chunks: stream end
        self.window.controller.chat.render.stream_end()

        # log
        self.log("End of stream.")

        # update ctx
        ctx.output = output
        ctx.set_tokens(ctx.input_tokens, output_tokens)

    def handle_complete(self, ctx: CtxItem):
        """
        Handle completed context

        :param ctx: CtxItem
        """
        mode = self.window.core.config.get('mode')
        self.window.core.ctx.post_update(mode)  # post update context, store last mode, etc.
        self.window.core.ctx.store()
        self.window.controller.ctx.update_ctx()  # update current ctx info

        extra_data = ""
        if ctx.is_vision:
            extra_data = " (VISION)"
        self.window.ui.status(
            trans('status.tokens') + ": {} + {} = {}{}".
            format(ctx.input_tokens, ctx.output_tokens, ctx.total_tokens, extra_data))

        # store to history
        if self.window.core.config.get('store_history'):
            self.window.core.history.append(ctx, "output")

    def handle_cmd(self, ctx: CtxItem):
        """
        Handle plugin commands

        :param ctx: CtxItem
        """
        cmds = self.window.core.command.extract_cmds(ctx.output)
        if len(cmds) > 0:
            ctx.cmds = cmds  # append to ctx
            if self.window.core.config.get('cmd'):
                self.log("Executing commands...")
                self.window.ui.status(trans('status.cmd.wait'))
                self.window.controller.plugins.apply_cmds(ctx, cmds)
            else:
                self.window.controller.plugins.apply_cmds_only(ctx, cmds)

    def log(self, data: any):
        """
        Log data to debug

        :param data: Data to log
        """
        self.window.controller.debug.log(data, True)
