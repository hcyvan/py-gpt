#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2023.12.27 14:00:00                  #
# ================================================== #

import json
import time

from sqlalchemy import text

from pygpt_net.item.ctx import CtxMeta, CtxItem


class Storage:
    def __init__(self, window=None):
        """
        Initialize storage instance

        :param window: Window instance
        """
        self.window = window

    def attach(self, window):
        """
        Attach window instance

        :param window: Window instance
        """
        self.window = window

    def get_meta(self):
        """
        Return dict with CtxMeta objects, indexed by ID

        :return: dict of CtxMeta
        :rtype: dict
        """
        stmt = text("""
            SELECT * FROM ctx_meta ORDER BY updated_ts DESC
        """)
        items = {}
        db = self.window.core.db.get_db()
        with db.connect() as conn:
            result = conn.execute(stmt)
            for row in result:
                meta = CtxMeta()
                self.unpack_meta(meta, row._asdict())
                items[meta.id] = meta
        return items

    def get_items(self, id):
        """
        Return ctx items list by ctx meta ID

        :return: list of CtxItem
        :rtype: list
        """
        stmt = text("""
            SELECT * FROM ctx_item WHERE meta_id = :id ORDER BY id ASC
        """).bindparams(id=id)
        items = []
        db = self.window.core.db.get_db()
        with db.connect() as conn:
            result = conn.execute(stmt)
            for row in result:
                item = CtxItem()
                self.unpack_item(item, row._asdict())
                items.append(item)
        return items

    def truncate_all(self):
        """
        Truncate all ctx tables

        :return: true if truncated
        :rtype: bool
        """
        db = self.window.core.db.get_db()
        with db.begin() as conn:
            conn.execute(text("DELETE FROM ctx_item"))
            conn.execute(text("DELETE FROM ctx_meta"))
        return True

    def delete_meta_by_id(self, id):
        """
        Delete ctx meta by ID

        :param id: ctx meta ID
        :return: true if deleted
        :rtype: bool
        """
        stmt = text("""
            DELETE FROM ctx_meta WHERE id = :id
        """).bindparams(id=id)
        db = self.window.core.db.get_db()
        with db.begin() as conn:
            conn.execute(stmt)
        self.delete_items_by_meta_id(id)
        return True

    def delete_items_by_meta_id(self, id):
        """
        Delete ctx items by ctx meta ID

        :param id: ctx meta ID
        :return: true if deleted
        :rtype: bool
        """
        stmt = text("""
            DELETE FROM ctx_item WHERE meta_id = :id
        """).bindparams(id=id)
        db = self.window.core.db.get_db()
        with db.begin() as conn:
            conn.execute(stmt)
        return True

    def update_meta(self, meta):
        """
        Update ctx meta

        :param meta: CtxMeta
        :return: true if updated
        :rtype: bool
        """
        db = self.window.core.db.get_db()
        stmt = text("""
            UPDATE ctx_meta 
            SET
                name = :name,
                mode = :mode,
                last_mode = :last_mode,
                thread_id = :thread_id,
                assistant_id = :assistant_id,
                preset_id = :preset_id,
                run_id = :run_id,
                status = :status,
                extra = :extra,
                is_initialized = :is_initialized,
                is_deleted = :is_deleted,
                is_important = :is_important,
                is_archived = :is_archived
            WHERE id = :id
        """).bindparams(
            id=meta.id,
            name=meta.name,
            mode=meta.mode,
            last_mode=meta.last_mode,
            thread_id=meta.thread,
            assistant_id=meta.assistant,
            preset_id=meta.preset,
            run_id=meta.run,
            status=meta.status,
            extra=meta.extra,
            is_initialized=int(meta.initialized),
            is_deleted=int(meta.deleted),
            is_important=int(meta.important),
            is_archived=int(meta.archived)
        )
        with db.begin() as conn:
            conn.execute(stmt)
            return True

    def update_meta_ts(self, id):
        """
        Update ctx meta updated timestamp

        :param id: ctx meta ID
        :return: true if updated
        :rtype: bool
        """
        db = self.window.core.db.get_db()
        ts = int(time.time())
        stmt = text("""
            UPDATE ctx_meta 
            SET
                updated_ts = :updated_ts
            WHERE id = :id
        """).bindparams(
            id=id,
            updated_ts=ts
        )
        with db.begin() as conn:
            conn.execute(stmt)
            return True

    def insert_meta(self, meta):
        """
        Insert ctx meta

        :param meta: CtxMeta
        :return: inserted record ID
        :rtype: int
        """
        db = self.window.core.db.get_db()
        ts = int(time.time())
        stmt = text("""
            INSERT INTO ctx_meta 
            (
                uuid,
                created_ts,
                updated_ts,
                name,
                mode,
                last_mode,
                thread_id,
                assistant_id,
                preset_id,
                run_id,
                status,
                extra,
                is_initialized,
                is_deleted,
                is_important,
                is_archived
            )
            VALUES 
            (
                :uuid,
                :created_ts,
                :updated_ts,
                :name,
                :mode,
                :last_mode,
                :thread_id,
                :assistant_id,
                :preset_id,
                :run_id,
                :status,
                :extra,
                :is_initialized,
                :is_deleted,
                :is_important,
                :is_archived
            )
        """).bindparams(
            uuid=meta.uuid,
            created_ts=ts,
            updated_ts=ts,
            name=meta.name,
            mode=meta.mode,
            last_mode=meta.last_mode,
            thread_id=meta.thread,
            assistant_id=meta.assistant,
            preset_id=meta.preset,
            run_id=meta.run,
            status=meta.status,
            extra=meta.extra,
            is_initialized=int(meta.initialized),
            is_deleted=int(meta.deleted),
            is_important=int(meta.important),
            is_archived=int(meta.archived)
        )
        with db.begin() as conn:
            result = conn.execute(stmt)
            meta.id = result.lastrowid
            return meta.id

    def insert_item(self, meta, item):
        """
        Insert ctx item

        :param meta: Context meta (CtxMeta)
        :param item: Context item (CtxItem)
        :return: inserted record ID
        :rtype: int
        """
        db = self.window.core.db.get_db()
        stmt = text("""
            INSERT INTO ctx_item 
            (
                meta_id,
                input,
                output,
                input_name,
                output_name,
                input_ts,
                output_ts,
                mode,
                thread_id,
                msg_id,
                run_id,
                results_json,
                urls_json,
                images_json,
                extra,
                input_tokens,
                output_tokens,
                total_tokens
            )
            VALUES 
            (
                :meta_id,
                :input,
                :output,
                :input_name,
                :output_name,
                :input_ts,
                :output_ts,
                :mode,
                :thread_id,
                :msg_id,
                :run_id,
                :results_json,
                :urls_json,
                :images_json,
                :extra,
                :input_tokens,
                :output_tokens,
                :total_tokens
            )
        """).bindparams(
            meta_id=int(meta.id),
            input=item.input,
            output=item.output,
            input_name=item.input_name,
            output_name=item.output_name,
            input_ts=int(item.input_timestamp or 0),
            output_ts=int(item.output_timestamp or 0),
            mode=item.mode,
            thread_id=item.thread,
            msg_id=item.msg_id,
            run_id=item.run_id,
            results_json=self.pack_item_value(item.results),
            urls_json=self.pack_item_value(item.urls),
            images_json=self.pack_item_value(item.images),
            extra=self.pack_item_value(item.extra),
            input_tokens=int(item.input_tokens or 0),
            output_tokens=int(item.output_tokens or 0),
            total_tokens=int(item.total_tokens or 0)
        )
        with db.begin() as conn:
            result = conn.execute(stmt)
            item.id = result.lastrowid

        return item.id

    def update_item(self, item):
        """
        Update ctx item

        :param item: Context item (CtxItem)
        :return: True if updated
        :rtype: bool
        """
        db = self.window.core.db.get_db()
        stmt = text("""
            UPDATE ctx_item SET
                input = :input,
                output = :output,
                input_name = :input_name,
                output_name = :output_name,
                input_ts = :input_ts,
                output_ts = :output_ts,
                mode = :mode,
                thread_id = :thread_id,
                msg_id = :msg_id,
                run_id = :run_id,
                results_json = :results_json,
                urls_json = :urls_json,
                images_json = :images_json,
                extra = :extra,
                input_tokens = :input_tokens,
                output_tokens = :output_tokens,
                total_tokens = :total_tokens
            WHERE id = :id
        """).bindparams(
            id=item.id,
            input=item.input,
            output=item.output,
            input_name=item.input_name,
            output_name=item.output_name,
            input_ts=int(item.input_timestamp or 0),
            output_ts=int(item.output_timestamp or 0),
            mode=item.mode,
            thread_id=item.thread,
            msg_id=item.msg_id,
            run_id=item.run_id,
            results_json=self.pack_item_value(item.results),
            urls_json=self.pack_item_value(item.urls),
            images_json=self.pack_item_value(item.images),
            extra=self.pack_item_value(item.extra),
            input_tokens=int(item.input_tokens or 0),
            output_tokens=int(item.output_tokens or 0),
            total_tokens=int(item.total_tokens or 0)
        )
        with db.begin() as conn:
            conn.execute(stmt)
        return True

    def pack_item_value(self, value):
        """
        Pack item value to JSON

        :param value: Value to pack
        :return: JSON string or value itself
        :rtype: str
        """
        if isinstance(value, (list, dict)):
            return json.dumps(value)
        return value

    def unpack_item_value(self, value):
        """
        Unpack item value from JSON

        :param value: Value to unpack
        :return: Unpacked value
        :rtype: dict or list or str
        """
        if value is None:
            return None
        try:
            return json.loads(value)
        except:
            return value

    def unpack_item(self, item, row):
        """
        Unpack item from DB row

        :param item: Context item (CtxItem)
        :param row: DB row
        :return: context item
        :rtype: CtxItem
        """
        item.id = int(row['id'])
        item.meta_id = int(row['meta_id'])
        item.input = row['input']
        item.output = row['output']
        item.input_name = row['input_name']
        item.output_name = row['output_name']
        item.input_timestamp = int(row['input_ts'] or 0)
        item.output_timestamp = int(row['output_ts'] or 0)
        item.mode = row['mode']
        item.thread = row['thread_id']
        item.msg_id = row['msg_id']
        item.run_id = row['run_id']
        item.results = self.unpack_item_value(row['results_json'])
        item.urls = self.unpack_item_value(row['urls_json'])
        item.images = self.unpack_item_value(row['images_json'])
        item.extra = self.unpack_item_value(row['extra'])
        item.input_tokens = int(row['input_tokens'] or 0)
        item.output_tokens = int(row['output_tokens'] or 0)
        item.total_tokens = int(row['total_tokens'] or 0)
        return item

    def unpack_meta(self, meta, row):
        """
        Unpack meta from DB row

        :param meta: Context meta (CtxMeta)
        :param row: DB row
        :return: context meta
        :rtype: CtxMeta
        """
        meta.id = int(row['id'])
        meta.uuid = row['uuid']
        meta.created = int(row['created_ts'])
        meta.updated = int(row['updated_ts'])
        meta.name = row['name']
        meta.mode = row['mode']
        meta.last_mode = row['last_mode']
        meta.thread = row['thread_id']
        meta.assistant = row['assistant_id']
        meta.preset = row['preset_id']
        meta.run = row['run_id']
        meta.status = row['status']
        meta.extra = row['extra']
        meta.initialized = bool(row['is_initialized'])
        meta.deleted = bool(row['is_deleted'])
        meta.important = bool(row['is_important'])
        meta.archived = bool(row['is_archived'])
        return meta