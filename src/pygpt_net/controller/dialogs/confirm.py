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

class Confirm:
    def __init__(self, window=None):
        """
        Confirmation dialogs controller

        :param window: Window instance
        """
        self.window = window

    def accept(self, type: str, id: any = None, parent_object=None):
        """
        Confirm dialog accept

        :param type: dialog type
        :param id: dialog object id
        :param parent_object: dialog parent object
        """
        self.window.ui.dialog['confirm'].close()

        # presets
        if type == 'preset_exists':
            self.window.controller.presets.editor.save(True)
        elif type == 'preset_delete':
            self.window.controller.presets.delete(id, True)
        elif type == 'preset_clear':
            self.window.controller.presets.clear(True)

        # ctx
        elif type == 'ctx_delete':
            self.window.controller.ctx.delete(id, True)
        elif type == 'ctx_delete_all':
            self.window.controller.ctx.delete_history(True)

        # images
        elif type == 'img_delete':
            self.window.controller.chat.image.delete(id, True)

        # attachments
        elif type == 'attachments.delete':
            self.window.controller.attachment.delete(id, True)
        elif type == 'attachments_uploaded.clear':
            self.window.controller.assistant.files.clear_files(True)
        elif type == 'attachments_uploaded.delete':
            self.window.controller.assistant.files.delete(id, True)
        elif type == 'attachments.clear':
            self.window.controller.attachment.clear(True)

        # files
        elif type == 'files.delete':
            self.window.controller.files.delete(id, True)

        # assistants
        elif type == 'assistant_delete':
            self.window.controller.assistant.delete(id, True)
        elif type == 'assistant_import':
            self.window.controller.assistant.import_api(True)
        elif type == 'assistant_import_files':
            self.window.controller.assistant.files.sync(True)

        # settings
        elif type == 'settings.defaults.user':
            self.window.controller.settings.editor.load_defaults_user(True)
        elif type == 'settings.defaults.app':
            self.window.controller.settings.editor.load_defaults_app(True)
        elif type == 'settings.dict.delete':
            self.window.controller.config.dictionary.delete_item(parent_object, id, True)

        # plugins
        elif type == 'plugin.settings.defaults.user':
            self.window.controller.plugins.settings.load_defaults_user(True)
        elif type == 'plugin.settings.defaults.app':
            self.window.controller.plugins.settings.load_defaults_app(True)

        # models
        elif type == 'models.editor.delete':
            self.window.controller.model.editor.delete_by_idx(id, True)
        elif type == 'models.editor.defaults.user':
            self.window.controller.model.editor.load_defaults_user(True)
        elif type == 'models.editor.defaults.app':
            self.window.controller.model.editor.load_defaults_app(True)

        # index
        elif type == 'idx.index.file':
            self.window.controller.idx.indexer.index_file_confirm(id)  # id = path
        elif type == 'idx.index.files.all':
            self.window.controller.idx.indexer.index_all_files(id, True)
        elif type == 'idx.index.db':
            self.window.controller.idx.indexer.index_ctx_meta_confirm(id)  # id = ctx_id
        elif type == 'idx.index.db.all':
            self.window.controller.idx.indexer.index_ctx_from_ts_confirm(id)
        elif type == 'idx.clear':
            self.window.controller.idx.indexer.clear(id, True)

    def dismiss(self, type: str, id: any):
        """
        Confirm dialog dismiss

        :param type: dialog type
        :param id: dialog object id
        """
        self.window.ui.dialog['confirm'].close()

    def accept_rename(self, type: str, id: any, name: str):
        """
        Update name of object

        :param type: dialog type
        :param id: dialog object id
        :param name: new name
        """
        if type == 'ctx':
            self.window.controller.ctx.update_name(id, name)
        elif type == 'attachment':
            self.window.controller.attachment.update_name(id, name)
        elif type == 'attachment_uploaded':
            self.window.controller.assistant.files.update_name(id, name)
        elif type == 'output_file':
            self.window.controller.files.update_name(id, name)
        elif type == 'notepad':
            self.window.controller.notepad.update_name(id, name, True)

    def dismiss_rename(self):
        """Dismiss rename dialog"""
        self.window.ui.dialog['rename'].close()
