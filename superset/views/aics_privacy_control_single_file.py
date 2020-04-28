
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.decorators import has_access, has_access_api
from flask_appbuilder.fieldwidgets import BS3TextFieldWidget
from flask_babel import gettext as __, lazy_gettext as _
from superset import appbuilder
from .base import (
    DeleteMixin,
    SupersetModelView,
)
from superset.models.user_attributes import UserAttribute
from wtforms import TextField, StringField


class BS3TextFieldROWidget(BS3TextFieldWidget):
    def __call__(self, field, **kwargs):
        kwargs['readonly'] = 'true'
        return super(BS3TextFieldROWidget, self).__call__(field, **kwargs)

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
        "user_id",
        "access_key",
    ]

    edit_form_extra_fields = {
        'username': TextField('username', widget=BS3TextFieldROWidget())
    }

    edit_columns = [
        "username",
        "access_key",
    ]
    show_columns = [
        "username",
        "access_key",
        "created_on",
        "changed_on",
        "changed_by_name",
    ]


appbuilder.add_separator("Security")

appbuilder.add_view(
    AccessKeyModelView,
    "List Access Keys",
    label=__("List Access Keys"),
    category="Security",
    category_label=__("Security"),
    icon="fa-table",
)
