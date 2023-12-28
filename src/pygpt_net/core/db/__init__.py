#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2023.12.27 21:00:00                  #
# ================================================== #

import os
import time

from sqlalchemy import create_engine, text

from pygpt_net.migrations import Migrations


class Database:
    def __init__(self, window=None):
        """
        Database provider
        """
        self.window = window
        self.db_path = None
        self.db_name = 'db.sqlite'
        self.engine = None
        self.initialized = False
        self.echo = True
        self.migrations = Migrations()

    def init(self):
        """
        Initialize database
        """
        if not self.initialized:
            self.db_path = os.path.join(self.window.core.config.path, self.db_name)
            self.prepare()

    def prepare(self):
        """
        Prepare database
        """
        self.engine = create_engine('sqlite:///{}'.format(self.db_path), echo=self.echo, future=True)
        if not self.is_installed():
            self.install()
        self.initialized = True

    def install(self):
        """
        Install database schema
        """
        with self.engine.begin() as conn:
            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS config (
                config_key TEXT PRIMARY KEY,
                config_value TEXT,
                created_ts INTEGER,
                updated_ts INTEGER
            );"""))
            print("[DB] Installed database: {}".format(self.db_path))

    def get_version(self):
        """
        Get database migration version

        :return: version string
        """
        return int(self.get_param("db_version") or 0)

    def get_db(self):
        """
        Get database engine

        :return: database engine
        """
        return self.engine

    def is_installed(self):
        """
        Check if database is installed

        :return: True if installed
        """
        if not os.path.exists(self.db_path):
            return False

        with self.engine.connect() as conn:
            result = conn.execute(text("""
            SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='config';
            """)).fetchone()
            return result[0] == 1

    def apply_migration(self, migration, conn, db_version):
        """
        Apply DB migration

        :param migration: migration object
        :param conn: database connection
        :param db_version: database version
        """
        migration.window = self.window
        migration_version = int(migration.__class__.__name__.replace('Version', ''))
        if migration_version > db_version:
            migration.up(conn)
            self.set_param_exec("db_version", migration_version, conn)
            print("[DB] Executed DB migration: {}".format(migration.__class__.__name__).replace('Version', ''))

    def migrate(self):
        """
        Apply all DB migrations
        """
        db_version = self.get_version()
        migrations = Migrations().get_versions()
        sorted_migrations = sorted(migrations, key=lambda m: m.__class__.__name__)

        self.init()
        with self.engine.begin() as conn:
            for migration in sorted_migrations:
                self.apply_migration(migration, conn, db_version)

    def get_param(self, key):
        """
        Get parameter from database

        :param key: parameter key
        :return: parameter value
        :rtype: str
        """
        self.init()

        with self.engine.connect() as conn:
            sel_stmt = text("SELECT config_value FROM config WHERE config_key = :key").bindparams(key=key)
            result = conn.execute(sel_stmt).fetchone()
            return result[0] if result else None

    def set_param(self, key, value):
        """
        Insert or update parameter in database

        :param key: parameter key
        :param value: parameter value
        """
        self.init()
        with self.engine.begin() as conn:
            self.set_param_exec(key, value, conn)

    def set_param_exec(self, key, value, conn):
        """
        Insert or update parameter in database

        :param key: parameter key
        :param value: parameter value
        :param conn: database connection
        """
        ts = int(time.time())
        sel_stmt = text("SELECT 1 FROM config WHERE config_key = :key").bindparams(key=key)
        result = conn.execute(sel_stmt).fetchone()

        if result:
            upd_stmt = text("""
                UPDATE config
                SET config_value = :value, updated_ts = :updated_ts
                WHERE config_key = :key
            """).bindparams(key=key, value=value, updated_ts=ts)
        else:
            upd_stmt = text("""
                INSERT INTO config (config_key, config_value, created_ts, updated_ts) 
                VALUES (:key, :value, :created_ts, :updated_ts)
            """).bindparams(key=key, value=value, created_ts=ts, updated_ts=ts)

        conn.execute(upd_stmt)

