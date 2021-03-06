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
"""add_access_key_to_user_attributes

Revision ID: 5ad4d4f30245
Revises: b6fa807eac07
Create Date: 2020-01-02 10:25:02.835661

Check following link for the the generation of DB migration file
https://github.com/ASUS-AICS/incubator-superset/blob/0.35/CONTRIBUTING.md#adding-a-db-migration

"""

# revision identifiers, used by Alembic.
revision = '5ad4d4f30245'
down_revision = 'b6fa807eac07'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('user_attribute', sa.Column('access_key', sa.String(36), nullable=True))


def downgrade():
    op.drop_column('user_attribute', 'access_key')
