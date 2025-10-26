from .models.user import User, UserPhone, UserMeta, Grade
from .base_schema import BaseSchema

class UserSchema(BaseSchema):
    class Meta:
        model = User
        # only = {'id', 'name', 'email'}
        # autocomputed_fields = {'id'}

class UserPhoneSchema(BaseSchema):
    class Meta:
        model = UserPhone
        # only = {}
        # autocomputed_fields= {}


class UserMetaSchema(BaseSchema):
    class Meta:
        model = UserMeta
        # only = {}
        # autocomputed_fields= {}


class GradeSchema(BaseSchema):
    class Meta:
        model = Grade
        # only = {}
        # autocomputed_fields= {}
