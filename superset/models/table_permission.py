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
import re
from datetime import datetime, timedelta

from flask_appbuilder import Model
from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    Integer,
    Date,
    DateTime,
    Boolean,
    Sequence,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from superset import security_manager
from superset.models.helpers import AuditMixinNullable

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
    Customized table permission control table

    Superset 0.35 leverage Flask AppBuilder Role/Permission for permission control
    However, it makes permission auto-revocation impossible.
    So we build this permission control table and with auto-revocation mechanism
    """

    __tablename__ = "aics_table_permission"
    id = Column(Integer, Sequence("aics_table_permission_id_seq"), primary_key=True)  # pylint: disable=invalid-name
    user_id = Column(Integer, ForeignKey("ab_user.id"))
    user = relationship(
        security_manager.user_model, backref="table_permissions", foreign_keys=[user_id]
    )

    apply_date = Column(Date, nullable=False, default=datetime.now().date())
    expire_date = Column(Date, nullable=False, default=datetime.now().date()+timedelta(days=6*365/12))
    force_terminate_date = Column(DateTime)
    is_active = Column(Boolean, default=True)

    table_permissions = relationship(
        security_manager.permissionview_model, secondary=assoc_tableperm_permissionview, backref="table_perm"
    )

    @property
    def username(self):
        return self.user.username

    @username.setter
    def username(self, value):
        pass

    @property
    def exp_or_terminate_date(self):
        if self.force_terminate_date != None:
            return f'{str(self.force_terminate_date.date())}(Forced)'
        return self.expire_date

    @exp_or_terminate_date.setter
    def exp_or_terminate_date(self, value):
        pass

    @property
    def table_permission_list(self):
        table_perm = [str(perm.view_menu) for perm in self.table_permissions]
        return ', '.join(table_perm)

    @table_permission_list.setter
    def table_permission_list(self, value):
        pass

    @property
    def status(self):
        if self.is_active:
            return 'Active'
        elif self.force_terminate_date != None:
            return 'Force Revoked'
        else:
            return 'Expired'

    @status.setter
    def status(self, value):
        pass
