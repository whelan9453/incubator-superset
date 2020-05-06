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
import logging
from datetime import datetime

from flask_appbuilder import Model
from sqlalchemy import Column, ForeignKey, Integer, String, Date, DateTime, Boolean
from sqlalchemy.orm import relationship

from superset import security_manager
from superset.models.helpers import AuditMixinNullable


class TablePermission(Model, AuditMixinNullable):

    """
    Custom attributes attached to the user.

    Extending the user attribute is tricky due to its dependency on the
    authentication typew an circular dependencies in Superset. Instead, we use
    a custom model for adding attributes.

    """

    __tablename__ = "table_permission"
    id = Column(Integer, primary_key=True)  # pylint: disable=invalid-name
    user_id = Column(Integer, ForeignKey("ab_user.id"))
    user = relationship(
        security_manager.user_model, backref="table_permissions", foreign_keys=[user_id]
    )

    table_id = Column(Integer, ForeignKey("tables.id"))
    apply_date = Column(Date, nullable=False, default=datetime.now())
    expire_date = Column(Date, nullable=False)
    force_treminate_date = Column(DateTime)
    is_active = Column(Boolean, default=True, nullable=False)

    @property
    def username(self):
        return self.user.username

    @username.setter
    def username(self, value):
        pass

    @property
    def table_names_with_id(self):
        return self._new_key

    @table_names_with_id.setter
    def table_names_with_id(self, value):
        self._new_key = value

    @property
    def changed_by_name(self):
        return self.changed_by_
