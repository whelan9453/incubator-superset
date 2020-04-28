from flask_appbuilder.fieldwidgets import BS3TextFieldWidget
from flask_appbuilder.forms import DynamicForm
from flask_babel import lazy_gettext as _

from wtforms import BooleanField, IntegerField, SelectField, StringField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from superset import app, db, security_manager
from superset.forms import CommaSeparatedListField, filter_not_empty_values
from superset.models import core as models

config = app.config

class BS3TextFieldROWidget(BS3TextFieldWidget):
    def __call__(self, field, **kwargs):
        kwargs['readonly'] = 'true'
        return super(BS3TextFieldROWidget, self).__call__(field, **kwargs)

class AccessKeyEditForm(DynamicForm):
    username = TextField(_('username'), widget=BS3TextFieldROWidget())
    access_key =  SelectField(_('access_key'),
        description=_(
            "If table exists do one of the following: "
            "Fail (do nothing), Replace (drop and recreate table) "
            "or Append (insert data)."
        ),
        choices=[
            ("fail", _("Fail")),
            ("replace", _("Replace")),
            ("append", _("Append")),
        ],
        validators=[DataRequired()],
    )