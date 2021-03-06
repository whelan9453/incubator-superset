# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# pylint: disable=C,R,W
import os
import functools
import inspect
import json
import logging
import textwrap
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, cast, Type

from flask import current_app, g, request

from applicationinsights import TelemetryClient


class AbstractEventLogger(ABC):
    @abstractmethod
    def log(self, user_id, action, *args, **kwargs):
        pass

    def log_this(self, f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            user_id = None
            if g.user:
                user_id = g.user.get_id()
            d = request.form.to_dict() or {}

            # request parameters can overwrite post body
            request_params = request.args.to_dict()
            d.update(request_params)
            d.update(kwargs)

            slice_id = d.get("slice_id")
            dashboard_id = d.get("dashboard_id")

            try:
                slice_id = int(
                    slice_id or json.loads(d.get("form_data")).get("slice_id")
                )
            except (ValueError, TypeError):
                slice_id = 0

            self.stats_logger.incr(f.__name__)
            start_dttm = datetime.now()
            value = f(*args, **kwargs)
            extra_info = {}
            if isinstance(value, tuple):
                extra_info = value[1]
                value = value[0]
            duration_ms = (datetime.now() - start_dttm).total_seconds() * 1000

            # bulk insert
            try:
                explode_by = d.get("explode")
                records = json.loads(d.get(explode_by))
            except Exception:
                records = [d]

            referrer = request.referrer[:1000] if request.referrer else None

            # pass user_id through extra_info when access throuth sql_csv_api
            if user_id == None:
                user_id = extra_info.get("user_id")

            self.log(
                user_id,
                f.__name__,
                records=records,
                dashboard_id=dashboard_id,
                slice_id=slice_id,
                duration_ms=duration_ms,
                referrer=referrer,
                database=extra_info.get("database"),
                schema=extra_info.get("schema"),
                tables=extra_info.get("tables"),
                sql=extra_info.get("sql"),
                err_msg=extra_info.get("err_msg"),
                log_msg=extra_info.get("log_msg")
            )
            return value

        return wrapper

    @property
    def stats_logger(self):
        return current_app.config.get("STATS_LOGGER")


def get_event_logger_from_cfg_value(cfg_value: object) -> AbstractEventLogger:
    """
    This function implements the deprecation of assignment of class objects to EVENT_LOGGER
    configuration, and validates type of configured loggers.

    The motivation for this method is to gracefully deprecate the ability to configure
    EVENT_LOGGER with a class type, in favor of preconfigured instances which may have
    required construction-time injection of proprietary or locally-defined dependencies.

    :param cfg_value: The configured EVENT_LOGGER value to be validated
    :return: if cfg_value is a class type, will return a new instance created using a
    default con
    """
    result: Any = cfg_value
    if inspect.isclass(cfg_value):
        logging.warning(
            textwrap.dedent(
                """
                In superset private config, EVENT_LOGGER has been assigned a class object. In order to
                accomodate pre-configured instances without a default constructor, assignment of a class
                is deprecated and may no longer work at some point in the future. Please assign an object
                instance of a type that implements superset.utils.log.AbstractEventLogger.
                """
            )
        )

        event_logger_type = cast(Type, cfg_value)
        result = event_logger_type()

    # Verify that we have a valid logger impl
    if not isinstance(result, AbstractEventLogger):
        raise TypeError(
            "EVENT_LOGGER must be configured with a concrete instance of superset.utils.log.AbstractEventLogger."
        )

    logging.info(f"Configured event logger of type {type(result)}")
    return cast(AbstractEventLogger, result)

INSTRUMENTATION_KEY=os.environ.get('INSTRUMENTATION_KEY')
tc = TelemetryClient(INSTRUMENTATION_KEY)
class DBEventLogger(AbstractEventLogger):
    def appinsights(self, data):
        print(f'appinsights triggerd with {data}')
        tc.track_event('medical.superset', data)
        tc.flush()
    
    def log(self, user_id, action, *args, **kwargs):
        from superset.models.core import Log

        records = kwargs.get("records", list())
        dashboard_id = kwargs.get("dashboard_id")
        slice_id = kwargs.get("slice_id")
        duration_ms = kwargs.get("duration_ms")
        referrer = kwargs.get("referrer")
        database = kwargs.get("database")
        schema = kwargs.get("schema")
        tables = kwargs.get("tables")
        sql = kwargs.get("sql")
        log_msg = kwargs.get("log_msg")
        err_msg = kwargs.get("err_msg")
        success = "true" if err_msg == None else "false"

        logs = list()
        for record in records:
            try:
                json_string = json.dumps(record)
            except Exception:
                json_string = None
            log = Log(
                action=action,
                json=json_string,
                dashboard_id=dashboard_id,
                slice_id=slice_id,
                duration_ms=duration_ms,
                referrer=referrer,
                user_id=user_id,
            )
            logs.append(log)
            json_log = {
                'level': 'info',
                'success': success,
                'state':'finish',
                'function': action,
                'json': json_string,
                'duration': duration_ms,
                'referrer': referrer,
                'user_id': user_id,
                'database': database,
                'schema': schema,
                'tables': tables,
                'sql': sql
                }
            if err_msg != None:
                json_log['err_msg'] = str(err_msg)

            if log_msg != None:
                json_log['log_msg'] = str(log_msg)

            self.appinsights(json_log)

        sesh = current_app.appbuilder.get_session
        sesh.bulk_save_objects(logs)
        sesh.commit()
