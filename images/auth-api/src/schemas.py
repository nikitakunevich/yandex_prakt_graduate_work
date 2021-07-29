from marshmallow import Schema, fields


class RootPasswordSchema(Schema):
    root_password = fields.String(required=True)


class IdTokenSchema(Schema):
    id_token = fields.String(required=True)


class IdTokenAuthSchema(Schema):
    id_token = fields.String(required=False)
    device_id = fields.UUID(required=False)
    recaptcha_response = fields.String(required=False)


class UserSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)
    first_name = fields.String(required=False)
    last_name = fields.String(required=False)


class UserAuthInfoSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True, default='google')
    device_id = fields.UUID(required=False)
    recaptcha_response = fields.String(required=False)


class RefreshTokenSchema(Schema):
    device_id = fields.UUID(required=True)
    refresh_token = fields.String(required=True)
    email = fields.Email(required=True)


class DeviceIdSchema(Schema):
    device_id = fields.UUID(required=False)


class DateRangeSchema(Schema):
    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime(required=True)


class RoleSchema(Schema):
    role_name = fields.String(required=True)


class UserRoleAssociationSchema(Schema):
    email = fields.Email(required=True)
    role_name = fields.String(required=True)