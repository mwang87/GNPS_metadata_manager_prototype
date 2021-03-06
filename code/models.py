# models.py
import datetime

from peewee import *

from app import db

class Filename(Model):
    filepath = TextField(primary_key=True)
    datasetaccession = TextField()

    class Meta:
        database = db

class Attribute(Model):
    categoryname = TextField(primary_key=True)

    class Meta:
        database = db

### Reference Parent Attribute
class AttributeTerm(Model):
    term = TextField(primary_key=True)

    class Meta:
        database = db

class Compound(Model):
    compoundname = TextField(primary_key=True)

    class Meta:
        database = db

class CompoundFilenameConnection(Model):
    compound = ForeignKeyField(Compound)
    filename = ForeignKeyField(Filename)

    class Meta:
        database = db
        primary_key = CompositeKey('compound', 'filename')

class CompoundTag(Model):
    tagname = TextField(primary_key=True)

    class Meta:
        database = db

class CompoundTagFilenameConnection(Model):
    compoundtag = ForeignKeyField(CompoundTag)
    filename = ForeignKeyField(Filename)

    class Meta:
        database = db
        primary_key = CompositeKey('compoundtag', 'filename')

class FilenameAttributeConnection(Model):
    filename = ForeignKeyField(Filename)
    attribute = ForeignKeyField(Attribute)
    attributeterm = ForeignKeyField(AttributeTerm)

    class Meta:
        database = db
        #@primary_key = False
        primary_key = CompositeKey('filename', 'attribute', 'attributeterm')
