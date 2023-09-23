from tortoise import models, fields


class User(models.Model):
    name = fields.TextField(pk=True)
    scopes = fields.JSONField()
    pass_hash = fields.TextField()


class Document(models.Model):
    ID = fields.IntField(pk=True)
    name = fields.TextField()
    creation_date = fields.DatetimeField(auto_now_add=True)
    deleted = fields.BooleanField(default=False)
    user = fields.ForeignKeyField('pg.User', related_name='document')


class Page(models.Model):
    ID = fields.IntField(pk=True)
    creation_date = fields.DatetimeField(auto_now_add=True)
    number = fields.IntField()
    path = fields.TextField()
    deleted = fields.BooleanField(default=False)
    keywords = fields.JSONField(null=True)
    document = fields.ForeignKeyField('pg.Document', 'page')


class Conversation(models.Model):
    ID = fields.IntField(pk=True)
    creation_date = fields.DatetimeField(auto_now_add=True)
    query = fields.TextField()
    answer = fields.UUIDField()
    positive = fields.BooleanField()
    user = fields.ForeignKeyField('pg.User')
