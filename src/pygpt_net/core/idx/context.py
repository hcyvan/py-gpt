#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.01.13 16:00:00                  #
# ================================================== #

from llama_index.llms import ChatMessage, MessageRole


class Context:
    def __init__(self, window=None):
        """
        Context core

        :param window: Window instance
        """
        self.window = window

    def get_messages(self, input_prompt, system_prompt):
        """
        Get messages from db

        :param input_prompt: input prompt
        :param system_prompt: system prompt
        :return: Messages
        """
        messages = []

        # tokens config
        model = self.window.core.config.get('model')
        model_id = self.window.core.models.get_id(model)
        mode = self.window.core.config.get('mode')

        used_tokens = self.window.core.tokens.from_user(input_prompt, system_prompt)  # threshold and extra included
        max_tokens = self.window.core.config.get('max_total_tokens')
        model_ctx = self.window.core.models.get_num_ctx(model_id)

        # fit to max model tokens
        if max_tokens > model_ctx:
            max_tokens = model_ctx

        if self.window.core.config.get('use_context'):
            items = self.window.core.ctx.get_prompt_items(model_id, mode, used_tokens, max_tokens)
            for item in items:
                # input
                if item.input is not None and item.input != "":
                    messages.append(ChatMessage(
                        role=MessageRole.USER,
                        content=item.input
                    ))
                # output
                if item.output is not None and item.output != "":
                    messages.append(ChatMessage(
                        role=MessageRole.ASSISTANT,
                        content=item.output
                    ))

        return messages
