from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, flash, url_for
from models import db, LBAVocabulaire, LBAUnit, LBALesson, LBAType, LBAV_VOCABULAIRE
from datetime import date
import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration DB avec echo des requêtes SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:sb@localhost/vocabCoreen'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # Affiche les requêtes SQL

db.init_app(app)

# Middleware pour vérifier les transactions
@app.after_request
def after_request(response):
    if db.session.is_active:
        logger.debug(f"Session active - dirty: {db.session.dirty}")
        if response.status_code >= 400:
            db.session.rollback()
            logger.warning("Rollback dû au code statut %d", response.status_code)
        else:
            try:
                db.session.commit()
                logger.info("Commit réussi après requête")
            except Exception as e:
                db.session.rollback()
                logger.error("Échec du commit: %s", str(e))
    return response

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        logger.debug("Données reçues: %s", request.form)
        
        try:
            # Validation des données
            data = {
                'id_unit': int(request.form['id_unit']),
                'id_lesson': int(request.form['id_lesson']),
                'id_type': int(request.form['id_type']),
                'voc_coreen': request.form['voc_coreen'],
                'voc_traduction': request.form['voc_traduction'],
                'exemple_coreen': request.form.get('exemple_coreen', ''),
                'exemple_traduit': request.form.get('exemple_traduit', '')
            }

            # Vérification des relations
            unit_exists = db.session.query(LBAUnit.query.filter_by(id_unit=data['id_unit']).exists()).scalar()
            lesson_exists = db.session.query(LBALesson.query.filter_by(id_lesson=data['id_lesson']).exists()).scalar()
            type_exists = db.session.query(LBAType.query.filter_by(id_type=data['id_type']).exists()).scalar()

            if not all([unit_exists, lesson_exists, type_exists]):
                missing = []
                if not unit_exists: missing.append(f"Unité {data['id_unit']}")
                if not lesson_exists: missing.append(f"Leçon {data['id_lesson']}")
                if not type_exists: missing.append(f"Type {data['id_type']}")
                flash(f"Éléments introuvables: {', '.join(missing)}", 'error')
            else:
                # Création et sauvegarde
                new_entry = LBAVocabulaire(
                    id_unit=data['id_unit'],
                    id_lesson=data['id_lesson'],
                    id_type=data['id_type'],
                    voc_coreen=data['voc_coreen'],
                    voc_traduction=data['voc_traduction'],
                    exemple_coreen=data['exemple_coreen'],
                    exemple_traduit=data['exemple_traduit'],
                    date_ajout=date.today()
                )
                
                db.session.add(new_entry)
                db.session.flush()  # Force l'insertion sans commit
                logger.info(f"Nouvelle entrée créée avec ID: {new_entry.id_voc}")
                
                flash('Enregistrement réussi!', 'success')

        except ValueError:
            flash('Veuillez entrer des IDs valides', 'error')
            logger.error("Erreur de conversion des IDs")
        except Exception as e:
            logger.error("Erreur fatale: %s", str(e), exc_info=True)
            flash("Erreur technique lors de l'enregistrement", 'error')

        return redirect(url_for('index'))

    # GET request
    units = LBAUnit.query.order_by(LBAUnit.id_unit).all()
    lessons = LBALesson.query.order_by(LBALesson.id_lesson).all()
    types = LBAType.query.order_by(LBAType.id_type).all()
    
    return render_template('index.html', units=units, lessons=lessons, types=types)


@app.route('/vocabulaire')
def liste_vocabulaire():
    try:
        # Récupération des paramètres de filtre
        filter_unit = request.args.get('unit')
        filter_lesson = request.args.get('lesson')
        filter_type = request.args.get('type')
        
        # Construction de la requête de base
        query = LBAV_VOCABULAIRE.query
        
        # Application des filtres
        if filter_unit and filter_unit != 'all':
            query = query.filter(LBAV_VOCABULAIRE.unit == filter_unit)
        if filter_lesson and filter_lesson != 'all':
            query = query.filter(LBAV_VOCABULAIRE.lesson == filter_lesson)
        if filter_type and filter_type != 'all':
            query = query.filter(LBAV_VOCABULAIRE.type == filter_type)
        
        # Tri et exécution
        mots = query.order_by(
            LBAV_VOCABULAIRE.unit, 
            LBAV_VOCABULAIRE.lesson,
            LBAV_VOCABULAIRE.voc_coreen
        ).all()
        
        # Récupération des valeurs distinctes pour les menus déroulants
        units = db.session.query(LBAV_VOCABULAIRE.unit).distinct().order_by(LBAV_VOCABULAIRE.unit).all()
        lessons = db.session.query(LBAV_VOCABULAIRE.lesson).distinct().order_by(LBAV_VOCABULAIRE.lesson).all()
        types = db.session.query(LBAV_VOCABULAIRE.type).distinct().order_by(LBAV_VOCABULAIRE.type).all()
        
        return render_template(
            'liste_vocabulaire.html',
            mots=mots,
            units=units,
            lessons=lessons,
            types=types,
            current_unit=filter_unit,
            current_lesson=filter_lesson,
            current_type=filter_type
        )
        
    except Exception as e:
        app.logger.error(f"Erreur : {str(e)}")
        flash("Erreur lors du chargement du vocabulaire", "error")
        return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Initialisation des données de base
        if not LBAUnit.query.first():
            db.session.add_all([
                LBAUnit(id_unit=1, unit="Unité 1 : Apprendre à lire"),
                LBAUnit(id_unit=2, unit="Unité 2 : Grammaire basique")
            ])
        
        if not LBALesson.query.first():
            db.session.add_all([
                LBALesson(id_lesson=1, lesson="Leçon 1 : Phrases basiques"),
                LBALesson(id_lesson=2, lesson="Leçon 2 : Particules")
            ])
        
        if not LBAType.query.first():
            db.session.add_all([
                LBAType(id_type=1, type="Nom"),
                LBAType(id_type=2, type="Verbe")
            ])
        
        try:
            db.session.commit()
            logger.info("Données initiales créées")
        except Exception as e:
            db.session.rollback()
            logger.error("Erreur initialisation: %s", str(e))

    app.run(debug=True)