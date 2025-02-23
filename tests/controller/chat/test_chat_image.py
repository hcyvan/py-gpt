#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.01.02 11:00:00                  #
# ================================================== #

import os
from unittest.mock import MagicMock, patch

from PySide6.QtWidgets import QFileDialog

from tests.mocks import mock_window
from pygpt_net.controller.chat.image import Image
from pygpt_net.item.ctx import CtxItem


def test_send(mock_window):
    """Test handle image"""
    image = Image(mock_window)

    mock_window.core.config.data['mode'] = 'img'
    mock_window.core.config.data['model'] = 'dall-e-3'
    mock_window.core.config.data['user_name'] = 'User'
    mock_window.core.config.data['ctx.auto_summary'] = True
    # mock_window.core.config.data['store_history'] = True

    result = True
    mock_window.core.gpt.call = MagicMock(return_value=result)
    mock_window.core.chain.call = MagicMock(return_value=result)

    with patch('PySide6.QtWidgets.QApplication.processEvents') as mock_process_events:

        ctx = image.send('message')

        # mock_window.core.history.append.assert_called_once()  # should append to history (?)
        mock_window.controller.chat.render.append_input.assert_called_once()  # should append input
        mock_window.controller.ctx.prepare_name.assert_called_once()  # should prepare name for ctx
        mock_window.core.image.generate.assert_called_once()  # should generate image

        assert ctx.input_name == 'User'  # should have input name
        assert ctx.input == 'message'  # should have input text


def test_handle_response(mock_window):
    image = Image(mock_window)
    image.open_images = MagicMock()

    mock_window.core.config.data['mode'] = 'img'
    mock_window.core.config.data['model'] = 'dall-e-3'
    mock_window.core.config.data['user_name'] = 'User'

    ctx = CtxItem()
    prompt = 'prompt'
    paths = ['path1', 'path2']

    image.handle_response(ctx, paths, prompt)

    image.open_images.assert_called_once_with(paths)  # should open images
    mock_window.core.ctx.post_update.assert_called_once()  # should post update context
    mock_window.controller.chat.render.append_output.assert_called_once()  # should append output
    mock_window.core.ctx.store.assert_called_once()  # should save current ctx to DB
    mock_window.ui.status.assert_called_once()  # should update status
    mock_window.core.ctx.update_item.assert_called_once()  # should update ctx in DB


def test_handle_response_inline(mock_window):
    image = Image(mock_window)
    image.open_images = MagicMock()

    mock_window.core.config.data['mode'] = 'img'
    mock_window.core.config.data['model'] = 'dall-e-3'
    mock_window.core.config.data['user_name'] = 'User'

    ctx = CtxItem()
    prompt = 'prompt'
    paths = ['path1', 'path2']

    image.handle_response_inline(ctx, paths, prompt)

    mock_window.core.ctx.update_item.assert_called_once()  # should update ctx in DB
    mock_window.ui.status.assert_called_once()  # should update status
    mock_window.controller.chat.render.append_extra.assert_called_once()  # should append extra output
    mock_window.controller.chat.render.to_end()  # should call render end method


def test_open_images(mock_window):
    image = Image(mock_window)
    mock_window.ui.dialog['image'] = MagicMock()
    paths = []
    image.open_images(paths)
    mock_window.ui.dialog['image'].show.assert_called_once()  # should show dialog


def test_open(mock_window):
    image = Image(mock_window)
    with patch('webbrowser.open') as mock:
        image.open('path')
        mock.assert_called_once_with('path')


def test_open_dir(mock_window):
    image = Image(mock_window)
    with patch('os.path.exists') as mock:
        image.open_dir('path')
        mock.assert_called_once_with('path')
        mock_window.controller.files.open_in_file_manager.assert_called_once_with('path')


def test_save(mock_window):
    image = Image(mock_window)
    QFileDialog.getSaveFileName = MagicMock(return_value=('path', 'path'))

    with patch('shutil.copyfile') as mock:
        image.save('path')
        mock.assert_called_once_with('path', 'path')
        mock_window.ui.status.assert_called_once()  # should update status


def test_delete(mock_window):
    image = Image(mock_window)
    # image.window.ui.dialogs.confirm = MagicMock()
    os.remove = MagicMock()
    image.delete('path', force=True)
    # image.window.ui.dialogs.confirm.assert_called_once()
    os.remove.assert_called_once_with('path')
