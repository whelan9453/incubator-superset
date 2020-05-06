from uuid import uuid4
from sqlalchemy.sql import exists
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.fieldwidgets import BS3TextFieldWidget, Select2Widget
from flask_appbuilder.security.sqla import models as ab_models
from flask_babel import gettext as __, lazy_gettext as _
from superset import appbuilder, db, event_logger, security_manager
from superset.views.base import (
    DeleteMixin,
    SupersetModelView,
)
from superset.models.user_attributes import UserAttribute
from superset.models.table_permission import TablePermission
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms import TextField, SelectField
from wtforms.validators import DataRequired

class BS3TextFieldROWidget(BS3TextFieldWidget):
    '''Inherent BS3TextFieldWidget and create a read only version
        ref: https://github.com/dpgaspar/Flask-AppBuilder/blob/master/docs/advanced.rst#forms---readonly-fields
    '''
    def __call__(self, field, **kwargs):
        kwargs['readonly'] = 'true'
        return super(BS3TextFieldROWidget, self).__call__(field, **kwargs)

def get_user_options():
    '''Get user list and filter out the ones already has a access key
        Used in the QuerySelectField of add form
    '''
    User = ab_models.User
    return db.session.query(User).filter(User.active == True).filter(~ exists().where(UserAttribute.user_id == User.id))

def get_table_perm_list():
    '''Get table list
        Used in the QuerySelectField of add form of TablePermission
    '''
    # get id of "datasource access" 
    # get all permission_id == "datasource access" from ab_permission_view
    # store the id into table
    perm_datasource_access = security_manager.find_permission('datasource_access')
    print(perm_datasource_access.name)
    pv_model = security_manager.permissionview_model
    return db.session.query(pv_model).filter(pv_model.permission_id == perm_datasource_access.id)

class AccessKeyModelView(SupersetModelView, DeleteMixin):
    datamodel = SQLAInterface(UserAttribute)

    list_columns = [
        "username",
        "access_key",
        "created_on",
        "changed_on",
        "changed_by_name",
    ]

    order_columns = ["user_id"]
    base_order = ("changed_on", "desc")

    label_columns = {
        "username": _("User"),
        "access_key": _("Access Key"),
        "created_on": _("Created On"),
        "changed_on": _("Changed On"),
        "changed_by_name": _("Changed By"),
    }

    add_columns = [
        "user",
        "access_key",
    ]

    add_form_extra_fields = {
        'user': QuerySelectField('User',
            query_factory=get_user_options,
            get_label='username',
            widget=Select2Widget()),
    }

    description_columns = {
        'access_key': 'DO NOT EDIT IT!! Auto-generated access key. Refresh page if you don\'t like it',
    }

    edit_form_extra_fields = {
        'username': TextField('User Name', widget=BS3TextFieldROWidget()),
        'access_key': TextField('Original Access Key', widget=BS3TextFieldROWidget()),
        'new_access_key': TextField('New Access Key',
            description=('Not editable, click "Save" to replace the access key with this new key.'),
            widget=BS3TextFieldROWidget()),
    }

    edit_columns = [
        "username",
        "access_key",
        "new_access_key",
    ]

    show_columns = [
        "username",
        "access_key",
        "created_on",
        "changed_on",
        "changed_by_name",
    ]

    @event_logger.log_this
    def pre_add(self, obj):
        obj.user_id = obj.user.id
        pass

    # Replace access_key with the new one for write back to DB
    @event_logger.log_this
    def pre_update(self, obj):
        obj.access_key = obj.new_access_key

    @event_logger.log_this
    def pre_delete(self, obj):
        print(f'delete access key of user: {obj.username}')

    # This function is used to generate new access key and fill in edit form
    def prefill_form(self, form, pk):
        form.new_access_key.data = str(uuid4())

class TablePermissionModelView(SupersetModelView, DeleteMixin):
    datamodel = SQLAInterface(TablePermission)
    list_columns = [
        "user",
        "table_permissions",
    ]
    order_columns = ["user"]
    # base_order = ("changed_on", "desc")
    label_columns = {
        "user": _("User"),
        "table_permissions": _("Table Permissions"),
        "avail_table_list": _("Table Permissions"),
        "created_on": _("Created On"),
        "changed_on": _("Changed On"),
        "changed_by_name": _("Changed By"),
    }
    add_columns = [
        "user",
        "table_permissions",
        # "tables",
        # "table_perm",
        # "expire_date",
        # "is_active",
    ]

    add_form_extra_fields = {
        'tables': QuerySelectField('Tables',
            query_factory=get_table_perm_list,
            widget=Select2Widget()),
        # 'expire_date': 
    }

appbuilder.add_separator("Security")

appbuilder.add_view(
    AccessKeyModelView,
    "Manage Access Keys",
    label=__("Manage Access Keys"),
    category="Security",
    category_label=__("Security"),
    icon="fa-key",
)

appbuilder.add_view(
    TablePermissionModelView,
    "Manage Table Permission",
    label=__("Manage Table Permission"),
    category="Security",
    category_label=__("Security"),
    icon="fa-list",
)
