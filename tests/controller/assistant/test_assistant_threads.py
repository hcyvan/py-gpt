#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.01.03 06:00:00                  #
# ================================================== #

import os
import webbrowser
from unittest.mock import MagicMock

from pygpt_net.item.assistant import AssistantItem
from pygpt_net.item.attachment import AttachmentItem
from pygpt_net.item.ctx import CtxItem
from tests.mocks import mock_window
from pygpt_net.controller.assistant.threads import Threads


def test_create_thread(mock_window):
    """Test create thread"""
    threads = Threads(mock_window)
    mock_window.core.gpt.assistants.thread_create = MagicMock(return_value="thread_id")
    mock_window.core.ctx.append_thread = MagicMock()
    threads.create_thread()
    mock_window.core.gpt.assistants.thread_create.assert_called_once()
    mock_window.core.ctx.append_thread.assert_called_once()

    assert mock_window.core.config.get("assistant_thread") == "thread_id"


def test_handle_messages(mock_window):
    """Test handle messages"""
    msg = MagicMock()
    msg.role = "assistant"
    msg.content = [MagicMock()]
    msg.content[0].text.value = "test"
    msg.content[0].text.type = "text"

    threads = Threads(mock_window)
    mock_window.core.gpt.assistants.msg_list = MagicMock(return_value=[msg])
    mock_window.controller.assistant.files.handle_received = MagicMock(return_value=["file_path"])
    mock_window.controller.chat.output.handle = MagicMock()
    mock_window.controller.chat.output.handle_cmd = MagicMock()
    mock_window.core.ctx.update_item = MagicMock()
    mock_window.controller.ctx.update = MagicMock()

    ctx = CtxItem()
    ctx.thread = "thread_id"
    threads.handle_messages(ctx)

    mock_window.core.gpt.assistants.msg_list.assert_called_once()
    mock_window.controller.assistant.files.handle_received.assert_called_once_with(ctx, msg)
    mock_window.controller.chat.output.handle.assert_called_once()
    mock_window.controller.chat.output.handle_cmd.assert_called_once()
    mock_window.core.ctx.update_item.assert_called()
    mock_window.controller.ctx.update.assert_called_once()

    assert ctx.files == ["file_path"]
    assert ctx.output == "test"


def test_handle_run(mock_window):
    """Test handle run"""
    threads = Threads(mock_window)
    mock_window.threadpool.start = MagicMock()

    ctx = CtxItem()
    threads.handle_run(ctx)

    mock_window.threadpool.start.assert_called_once()


def handle_status_complete(mock_window):
    """Test handle status complete"""
    threads = Threads(mock_window)
    mock_window.controller.chat.common.unlock_input = MagicMock()
    mock_window.statusChanged.emit = MagicMock()

    ctx = CtxItem()
    ctx.thread = "thread_id"
    threads.handle_status("completed", ctx)

    mock_window.controller.chat.common.unlock_input.assert_called_once()
    mock_window.statusChanged.emit.assert_called_once()

    assert threads.stop is False


def handle_status_failed(mock_window):
    """Test handle status failed"""
    threads = Threads(mock_window)
    mock_window.controller.chat.common.unlock_input = MagicMock()
    mock_window.statusChanged.emit = MagicMock()

    ctx = CtxItem()
    ctx.thread = "thread_id"
    threads.handle_status("failed", ctx)

    mock_window.controller.chat.common.unlock_input.assert_called_once()
    mock_window.statusChanged.emit.assert_called_once()

    assert threads.stop is False


def handle_status_common(mock_window):
    """Test handle status common"""
    threads = Threads(mock_window)
    mock_window.controller.chat.common.unlock_input = MagicMock()
    mock_window.statusChanged.emit = MagicMock()

    ctx = CtxItem()
    ctx.thread = "thread_id"
    threads.handle_status("other", ctx)

    mock_window.controller.chat.common.unlock_input.assert_not_called()


def test_handle_destroy(mock_window):
    """Test handle destroy"""
    threads = Threads(mock_window)
    threads.started = True
    threads.stop = True
    threads.handle_destroy()
    assert threads.started is False
    assert threads.stop is False


def test_handle_started(mock_window):
    """Test handle started"""
    threads = Threads(mock_window)
    mock_window.statusChanged = MagicMock()
    threads.handle_started()
    mock_window.statusChanged.emit.assert_called_once()
