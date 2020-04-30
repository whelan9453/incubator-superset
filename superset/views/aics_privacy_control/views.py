from uuid import uuid4
from sqlalchemy.sql import exists
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.fieldwidgets import BS3TextFieldWidget
from flask_appbuilder.security.sqla import models as ab_models
from flask_babel import gettext as __, lazy_gettext as _
from superset import appbuilder, db, event_logger
from superset.views.base import (
    DeleteMixin,
    SupersetModelView,
)
from superset.models.user_attributes import UserAttribute
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms import TextField, SelectField
from wtforms.validators import DataRequired

from uuid import uuid4


class BS3TextFieldROWidget(BS3TextFieldWidget):
    def __call__(self, field, **kwargs):
        kwargs['readonly'] = 'true'
        return super(BS3TextFieldROWidget, self).__call__(field, **kwargs)

def get_user_options():
    User = ab_models.User
    return db.session.query(User).filter(User.active == True).filter(~ exists().where(UserAttribute.user_id == User.id))

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
            get_label='username'),
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

    def pre_add(self, obj):
        obj.user_id = obj.user.id

    # Replace access_key with the new one
    def pre_update(self, obj):
        obj.access_key = obj.new_access_key

    # This function is used to generate new access key in edit form
    def prefill_form(self, form, pk):
        form.new_access_key.data = str(uuid4())

appbuilder.add_separator("Security")

appbuilder.add_view(
    AccessKeyModelView,
    "Manage Access Keys",
    label=__("Manage Access Keys"),
    category="Security",
    category_label=__("Security"),
    icon="fa-key",
)
