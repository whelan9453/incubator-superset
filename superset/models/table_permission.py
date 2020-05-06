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
import re
from datetime import datetime, timedelta

from flask_appbuilder import Model
from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    Integer,
    String,
    Date,
    DateTime,
    Boolean,
    Sequence,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from superset import security_manager
from superset.models.helpers import AuditMixinNullable


# class TablePermission(Model, AuditMixinNullable):

#     """
#     Custom attributes attached to the user.

#     Extending the user attribute is tricky due to its dependency on the
#     authentication typew an circular dependencies in Superset. Instead, we use
#     a custom model for adding attributes.

#     """

#     __tablename__ = "table_permission"
#     id = Column(Integer, primary_key=True)  # pylint: disable=invalid-name
#     user_id = Column(Integer, ForeignKey("ab_user.id"))
#     user = relationship(
#         security_manager.user_model, backref="user_table_perm", foreign_keys=[user_id]
#     )

#     # table_id = Column(Integer, ForeignKey("tables.id"))
#     table_perm_id = Column(Integer, ForeignKey("ab_permission_view.id"))
#     table_perm = relationship(
#         security_manager.permissionview_model, backref="table_perm", foreign_keys=[table_perm_id]
#     )
#     apply_date = Column(Date, nullable=False, default=datetime.now())
#     expire_date = Column(Date, nullable=False)
#     force_treminate_date = Column(DateTime)
#     is_active = Column(Boolean, default=True, nullable=False)

#     @property
#     def username(self):
#         return self.user.username

#     @username.setter
#     def username(self, value):
#         pass

#     @property
#     def table_names_with_id(self):
#         return self._new_key

#     @table_names_with_id.setter
#     def table_names_with_id(self, value):
#         self._new_key = value

#     @property
#     def changed_by_name(self):
#         return self.changed_by_


# class TablePermission2PermissionView(Model, AuditMixinNullable):

#     """

#     """

#     __tablename__ = "aics_tableperm_permissionview"
#     id = Column(Integer, Sequence("aics_tableperm_permissionview_id_seq"), primary_key=True) 
#     tableperm_id = Column(Integer, ForeignKey("aics_table_permission.id"))
#     permissionview_id = Column(Integer, ForeignKey("ab_permission_view.id"))
#     permissionview = relationship(
#         security_manager.permissionview_model, backref="tableperm_permissionview", foreign_keys=[permissionview_id]
#     )

#     def __repr__(self):
#         if self.is_active:
#             return re.sub(r'.* ', '', self.permissionview)+str(self.expire_date)
#         else:
#             return ''

assoc_tableperm_permissionview = Table(
    "aics_tableperm_permissionview",
    Model.metadata,
    Column('id', Integer, Sequence("aics_tableperm_permissionview_id_seq"), primary_key=True) ,
    Column('tableperm_id', Integer, ForeignKey("aics_table_permission.id")),
    Column('permissionview_id', Integer, ForeignKey("ab_permission_view.id")),
    UniqueConstraint("tableperm_id", "permissionview_id"),
)

class TablePermission(Model, AuditMixinNullable):

    """

    """

    __tablename__ = "aics_table_permission"
    id = Column(Integer, Sequence("aics_table_permission_id_seq"), primary_key=True)  # pylint: disable=invalid-name
    user_id = Column(Integer, ForeignKey("ab_user.id"))
    user = relationship(
        security_manager.user_model, backref="user_table_perm", foreign_keys=[user_id]
    )

    apply_date = Column(Date, nullable=False, default=datetime.now())
    expire_date = Column(Date, nullable=False, default=datetime.now()+timedelta(days=6*365/12))
    force_treminate_date = Column(DateTime)
    is_active = Column(Boolean, default=True, nullable=False)

    table_permissions = relationship(
        security_manager.permissionview_model, secondary=assoc_tableperm_permissionview, backref="table_perm"
    )

    # @property
    # def expire_date(self):
    #     return self._exp_date

    # @expire_date.setter
    # def expire_date(self, exp_date):
    #     self._exp_date = exp_date
    #     print(str(len(self.table_permissions)))
    #     for permission in self.table_permissions:
    #         print(permission)
    #         permission.expire_date = exp_date