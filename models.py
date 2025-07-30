from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

db = SQLAlchemy()

class LBAUnit(db.Model):
    __tablename__ = 'lba_unit_vocabulaire'
    id_unit = db.Column(db.Integer, primary_key=True)
    unit = db.Column(db.String(255))

class LBALesson(db.Model):
    __tablename__ = 'lba_lesson_vocabulaire'
    id_lesson = db.Column(db.Integer, primary_key=True)
    lesson = db.Column(db.String(255))

class LBAType(db.Model):
    __tablename__ = 'lba_type_vocabulaire'
    id_type = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(255))

class LBAVocabulaire(db.Model):
    __tablename__ = 'lba_vocabulaire'
    id_voc = db.Column(db.Integer, primary_key=True)
    id_unit = db.Column(db.Integer, db.ForeignKey('lba_unit_vocabulaire.id_unit'))
    id_lesson = db.Column(db.Integer, db.ForeignKey('lba_lesson_vocabulaire.id_lesson'))
    id_type = db.Column(db.Integer, db.ForeignKey('lba_type_vocabulaire.id_type'))
    voc_coreen = db.Column(db.Text)
    voc_traduction = db.Column(db.Text)
    exemple_coreen = db.Column(db.Text)
    exemple_traduit = db.Column(db.Text)
    date_ajout = db.Column(db.Date)
    
class LBAV_VOCABULAIRE(db.Model):
    __tablename__ = 'lbav_vocabulaire'
    
    # Suppression de primary_key=True et de __table_args__
    unit = db.Column(db.String(255))
    lesson = db.Column(db.String(255))
    type = db.Column(db.String(255))
    voc_coreen = db.Column(db.Text)
    voc_traduction = db.Column(db.Text)
    exemple_coreen = db.Column(db.Text)
    exemple_traduit = db.Column(db.Text)

    # Ajout d'une clé primaire composite explicite
    __mapper_args__ = {
        'primary_key': [unit, lesson, voc_coreen]
    }