from flask import g
from flask.ext.babel import lazy_gettext as l_
from flask_wtf import Form

from formencode.validators import URL
from sprox.formbase import EditableForm, Field
from sprox.widgets import PropertySingleSelectField
from tw.forms import TextField
from wtforms import TextField as _TextField, SelectField as _SelectField
from wtforms.validators import InputRequired, ValidationError

from .bootstrap import BootstrapForm
from skylines import db
from skylines.model import Club
from skylines.lib.validators import UniqueValueUnless


class SelectField(PropertySingleSelectField):
    def _my_update_params(self, d, nullable=False):
        query = db.session.query(Club.id, Club.name).order_by(Club.name)
        options = [(None, 'None')] + query.all()
        d['options'] = options
        return d

    def validate(self, value, *args, **kw):
        if isinstance(value, Club):
            value = value.id
        return super(SelectField, self).validate(value, *args, **kw)


def filter_club_id(model):
    return model.id == g.club_id


class EditForm(EditableForm):
    __base_widget_type__ = BootstrapForm
    __model__ = Club
    __hide_fields__ = ['id']
    __limit_fields__ = ['name', 'website']
    __field_widget_args__ = {
        'name': dict(label_text=l_('Name')),
        'website': dict(label_text=l_('Website')),
    }

    name = Field(TextField, UniqueValueUnless(filter_club_id, db.session, __model__, 'name'))
    website = Field(TextField, URL())

edit_form = EditForm(db.session)


class ClubsSelectField(_SelectField):
    def __init__(self, *args, **kwargs):
        super(ClubsSelectField, self).__init__(*args, **kwargs)
        self.coerce = int

    def process(self, *args, **kwargs):
        users = Club.query().order_by(Club.name)
        self.choices = [(0, '[' + l_('No club') + ']')]
        self.choices.extend([(user.id, user) for user in users])

        super(ClubsSelectField, self).process(*args, **kwargs)


class ChangeClubForm(Form):
    club = ClubsSelectField(l_('Club'))


class CreateClubForm(Form):
    name = _TextField(l_('Name'), validators=[InputRequired()])

    def validate_name(form, field):
        if Club.exists(name=field.data):
            raise ValidationError(l_('A club with this name exists already.'))
