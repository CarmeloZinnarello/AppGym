from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from ..models import db, User, Parametri, Scheda, Tipoesercizi, EserciziScheda,Appuntamenti, Check
from werkzeug.security import generate_password_hash 
from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy import desc
import os 
import openpyxl
from flask import request, redirect, url_for
import pandas as pd
from collections import defaultdict

bp = Blueprint('admin', __name__, url_prefix='/admin')

UPLOAD_LOGO = 'app/static'
if not os.path.exists(UPLOAD_LOGO):
    os.makedirs(UPLOAD_LOGO) 
UPLOAD_FOLDERParam = 'app/static/uploads/parameters'

UPLOAD_FOLDER = 'app/static/uploads/user'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER) 
UPLOAD_FOLDERParam = 'app/static/uploads/parameters'
if not os.path.exists(UPLOAD_FOLDERParam):
    os.makedirs(UPLOAD_FOLDERParam) 
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
@login_required
def dashboard():
    if not current_user.is_admin and not current_user.is_worker:
        return redirect(url_for('home.home'))
    return render_template('admin.html')


@bp.route('/users')
@login_required
def manage_users():
    if not current_user.is_admin and not current_user.is_worker:
        return redirect(url_for('home.home'))
    if current_user.is_admin :
        users = User.query.order_by(User.username).all()
    else :
        users = User.query.filter_by(is_admin=False, is_worker= False).order_by(User.username).all()
    return render_template('admin_users.html', users=users)

@bp.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_admin and not current_user.is_worker:
        return redirect(url_for('home.home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        nome = request.form['nome']
        cognome = request.form['cognome']
        cf = request.form['cf']
        sesso = request.form['sesso']
        manuale = request.files['manuale']
        is_admin = 'is_admin' in request.form
        is_active = 'is_active' in request.form
        is_worker = 'is_worker' in request.form
        alimentare = request.files['alimentare']
        integrazione  = request.files['integrazione']
        # Controllo se lo username esiste già
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Errore: Username già esistente!", "error")
            return redirect(url_for('admin.add_user'))
   
        # Creazione del nuovo utente con associazione al team
        new_user = User(username=username, password=generate_password_hash(password), is_admin=is_admin, is_active=is_active, is_worker = is_worker,
                        nome = nome, cognome = cognome, sesso = sesso, cf = cf)
        
        if manuale and allowed_file(manuale.filename):
            ext = manuale.filename.rsplit('.', 1)[1].lower()  # Estrai l'estensione del file
            manuale_filename = f"{username}_manuale.{ext}"
            manuale.save(os.path.join(UPLOAD_FOLDER, manuale_filename))

        if alimentare and allowed_file(alimentare.filename):
            ext = alimentare.filename.rsplit('.', 1)[1].lower()  # Estrai l'estensione del file
            alimentare_filename = f"{username}_alimentare.{ext}"
            alimentare.save(os.path.join(UPLOAD_FOLDER, alimentare_filename))

        if integrazione and allowed_file(integrazione.filename):
            ext = integrazione.filename.rsplit('.', 1)[1].lower()  # Estrai l'estensione del file
            integrazione_filename = f"{username}_integrazione.{ext}"
            integrazione.save(os.path.join(UPLOAD_FOLDER, integrazione_filename))

        db.session.add(new_user)
        db.session.commit()

        flash("Utente aggiunto con successo!", "success")
        return redirect(url_for('admin.manage_users'))

    return render_template('add_user.html')


@bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin and not current_user.is_worker:
        return redirect(url_for('home.home'))
    user = User.query.get(user_id)
    if user:
        if current_user.is_worker and user.is_admin :
            flash('Non puoi eliminare un account Admin!', 'error')
        else :
            db.session.delete(user)
            db.session.commit()
            flash('Utente eliminato con successo!', 'success')
    return redirect(url_for('admin.manage_users'))

@bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin and not current_user.is_worker:
        return redirect(url_for('home.home'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form['username']
       
        password = request.form['password']
        eraAttivo = user.is_active
        if password:
            user.password = generate_password_hash(password)
        user.is_admin = 'is_admin' in request.form
        user.is_active = 'is_active' in request.form
        user.nome = request.form['nome']
        user.cognome = request.form['cognome']
        user.cf = request.form['cf']
        user.sesso = request.form['sesso']
        user.is_admin = 'is_admin' in request.form
        user.is_active = 'is_active' in request.form
        user.is_worker = 'is_worker' in request.form
        manuale = request.files['manuale']
        alimentare = request.files['alimentare']
        integrazione  = request.files['integrazione']   
        if manuale and allowed_file(manuale.filename):
            ext = manuale.filename.rsplit('.', 1)[1].lower()  # Estrai l'estensione del file
            manuale_filename = f"{user.username}_manuale.{ext}"
            manuale.save(os.path.join(UPLOAD_FOLDER, manuale_filename))

        if alimentare and allowed_file(alimentare.filename):
            ext = alimentare.filename.rsplit('.', 1)[1].lower()  # Estrai l'estensione del file
            alimentare_filename = f"{user.username}_alimentare.{ext}"
            alimentare.save(os.path.join(UPLOAD_FOLDER, alimentare_filename))

        if integrazione and allowed_file(integrazione.filename):
            ext = integrazione.filename.rsplit('.', 1)[1].lower()  # Estrai l'estensione del file
            integrazione_filename = f"{user.username}_integrazione.{ext}"
            integrazione.save(os.path.join(UPLOAD_FOLDER, integrazione_filename))
        if(eraAttivo and user.is_active == False and current_user.is_worker) :
            flash('Non puoi disattivare un account Admin!', 'error')
        else:
            db.session.commit()
            flash('Utente aggiornato con successo!', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('edit_user.html', user=user)

@bp.route('/manage_parameters', methods=['GET', 'POST'])
@login_required
def manage_parameters():
    if not current_user.is_admin:
        return redirect(url_for('home.home'))  # Reindirizza gli utenti normali alla home

    # Recupera i parametri se esistono, altrimenti li crea con valori predefiniti
    parametri = Parametri.query.first()
  
    if parametri is None:
        parametri = Parametri(
            titolo="default"
        )
        db.session.add(parametri)
        db.session.commit()

    if request.method == 'POST':
        # Aggiorna i campi dai dati del form
        parametri.titolo = request.form.get('titolo', parametri.titolo)
        parametri.sliderPaginaPrincipale = request.form.get('sliderPaginaPrincipale', parametri.sliderPaginaPrincipale)
        parametri.banner = request.form.get('banner', parametri.banner)
        parametri.domanda1 = request.form.get('domanda1', parametri.domanda1)
        parametri.domanda2 = request.form.get('domanda2', parametri.domanda2)
        parametri.domanda3 = request.form.get('domanda3', parametri.domanda3)
        parametri.domanda4 = request.form.get('domanda4', parametri.domanda4)
        parametri.domanda5 = request.form.get('domanda5', parametri.domanda5)
        parametri.domanda6 = request.form.get('domanda6', parametri.domanda6)
        parametri.domanda7 = request.form.get('domanda7', parametri.domanda7)
        parametri.domanda8 = request.form.get('domanda8', parametri.domanda8)
        parametri.domanda9 = request.form.get('domanda9', parametri.domanda9)
        parametri.domanda10 = request.form.get('domanda10', parametri.domanda10)

        if 'immaginePaginaPrincipale' in request.files:
            file = request.files['immaginePaginaPrincipale']
            if file and allowed_file(file.filename):
                filename = 'logo.png'
                filepath = os.path.join(UPLOAD_LOGO, filename)
                file.save(filepath)

        db.session.commit()
        flash("Parametri aggiornati con successo!", "success")
        return redirect(url_for('admin.manage_parameters'))

    return render_template('manage_parameters.html', parametri=parametri)

@bp.route("/Schede", methods=["GET"])
@bp.route("/Schede/<int:user_id>", methods=["GET"])
@login_required
def manage_schede(user_id=None):
    if not current_user.is_admin:
        return redirect(url_for('home.home'))

    query = Scheda.query

    if user_id:
        query = query.filter(Scheda.userid == user_id)

    schede = query.order_by(Scheda.userid.asc(), Scheda.numero.asc(),Scheda.data_fine.asc()).all()

    return render_template("schede.html", schede=schede, user_id=user_id)

@bp.route("/schede/add/<int:user_id>", methods=["GET", "POST"])
@bp.route("/schede/add/", methods=["GET", "POST"])  # Percorso senza user_id
@login_required
def add_scheda(user_id = None):
    if user_id != None :
        selected_user = User.query.get_or_404(user_id)

    else :
        selected_user = None
   
    user = User.query.filter_by(is_admin = False, is_active = True).all()
    if request.method == "POST":
        # Recupera i dati dal modulo
        titolo = request.form.get("titolo")
        data_inizio_str = request.form.get("data_inizio")
        data_fine_str = request.form.get("data_fine")

        # Recupera il user_id selezionato
        user_fromform = request.form.get("user_id")  # user_id sarà una stringa, quindi potresti volerlo convertire in int
        if user_fromform:
            user_fromform = int(user_fromform)
        prossimaScheda = 1
        scheda_max = Scheda.query.filter_by(userid=user_fromform).order_by(desc(Scheda.numero)).first()
        if scheda_max:
            prossimaScheda = scheda_max.numero +1
        # Converte le date
        data_inizio = datetime.strptime(data_inizio_str, "%Y-%m-%d").date() if data_inizio_str else None
        data_fine = datetime.strptime(data_fine_str, "%Y-%m-%d").date() if data_fine_str else None
        is_active = 'is_active' in request.form
        # Verifica se tutti i campi obbligatori sono stati compilati
        if not titolo or not data_inizio or not user_fromform :
            flash("Compila tutti i campi obbligatori", "danger")
            return redirect(url_for("admin.add_scheda"))

        # Recupera l'utente selezionato (se esiste)
        user = User.query.get_or_404(user_fromform)

        # Crea una nuova scheda
        nuova_scheda = Scheda(
            titolo=titolo,
            numero=prossimaScheda,
            data_inizio=data_inizio,
            data_fine=data_fine,
            is_active = is_active,
            userid=user_fromform  # Salva l'user_id selezionato nella scheda
        )

        # Aggiungi la nuova scheda al database
        db.session.add(nuova_scheda)
        db.session.commit()

        flash(f"Scheda creata per {user.nome} {user.cognome}", "success")
        return redirect(url_for("admin.manage_schede"))

    return render_template("add_scheda.html", user = user, selected_user=selected_user)

@bp.route('/schede/delete/<int:scheda_id>', methods=['POST'])
@login_required
def delete_scheda(scheda_id):
    if not current_user.is_admin and not current_user.is_worker:
        flash('Non puoi fare questa operazione!', 'error')
        return redirect(url_for('home.home'))
    scheda = Scheda.query.get(scheda_id)
    if scheda:
       
            db.session.delete(scheda)
            db.session.commit()
            flash('Scheda eliminata con successo!', 'success')
    return redirect(url_for('admin.manage_schede'))



@bp.route("/schede/modifica/<int:scheda_id>", methods=["GET", "POST"])
@login_required
def modifica_scheda(scheda_id):
    scheda = Scheda.query.get_or_404(scheda_id)
    users = User.query.all()  # Recupera tutti gli utenti per il campo select
    
    if request.method == "POST":
        # Recupera i nuovi valori dal form
       
        titolo = request.form.get("titolo")
        data_inizio_str = request.form.get("data_inizio")
        data_fine_str = request.form.get("data_fine")
        is_active = 'is_active' in request.form
        # Converte le date
        data_inizio = datetime.strptime(data_inizio_str, "%Y-%m-%d").date() if data_inizio_str else None
        data_fine = datetime.strptime(data_fine_str, "%Y-%m-%d").date() if data_fine_str else None
        
        # Aggiorna la scheda
       
        scheda.titolo = titolo
        scheda.data_inizio = data_inizio
        scheda.data_fine = data_fine
        scheda.is_active = is_active
        # Salva le modifiche
        db.session.commit()

        flash("Scheda aggiornata con successo", "success")
        return redirect(url_for("admin.manage_schede"))

    # Restituisce il template con la scheda e gli utenti
    return render_template("edit_scheda.html", scheda=scheda, users=users)




@bp.route('/tipoesercizi', methods=['GET', 'POST'])
def gestione_tipoesercizi():
    if request.method == 'POST':
        nuovo = Tipoesercizi(
            nome=request.form.get('nome'),
            link=request.form.get('link'),
            tipo=request.form.get('tipo')
        )
        db.session.add(nuovo)
        db.session.commit()
        return redirect(url_for('admin.gestione_tipoesercizi'))

    lista = Tipoesercizi.query.order_by(Tipoesercizi.nome).all()
    return render_template('tipoesercizi.html', lista=lista)


@bp.route('/tipoesercizi/delete/<int:id>')
def elimina_tipoesercizi(id):
    record = Tipoesercizi.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('admin.gestione_tipoesercizi'))

TIPI_VALIDI = ['Gambe', 'Petto', 'Schiena', 'Spalle', 'Braccia', 'Core', 'Stretching']

@bp.route('/tipoesercizi/upload', methods=['POST'])
def upload_excel_tipoesercizi():
    file = request.files.get('file')

    if not file or not file.filename.lower().endswith('.csv'):
        flash('Carica un file CSV valido')
        return redirect(url_for('admin.gestione_tipoesercizi'))

    try:
        df = pd.read_csv(file)
    except Exception as e:
        flash(f'Errore lettura CSV: {e}')
        return redirect(url_for('admin.gestione_tipoesercizi'))

    # normalizza nomi colonne
    df.columns = df.columns.str.lower().str.strip()

    colonne_richieste = {'nome', 'link', 'tipo'}
    if not colonne_richieste.issubset(df.columns):
        flash('Il CSV deve contenere le colonne: nome, link, tipo')
        return redirect(url_for('admin.gestione_tipoesercizi'))

    inseriti = 0

    for _, row in df.iterrows():
        nome = row['nome']
        link = row['link']
        tipo = row['tipo']

        if pd.isna(nome) or tipo not in TIPI_VALIDI:
            continue

        if Tipoesercizi.query.filter_by(nome=nome).first():
            continue

        db.session.add(Tipoesercizi(
            nome=str(nome).strip(),
            link=None if pd.isna(link) else str(link).strip(),
            tipo=tipo
        ))
        inseriti += 1

    db.session.commit()
    flash(f'Import CSV completato: {inseriti} record inseriti')
    return redirect(url_for('admin.gestione_tipoesercizi'))


@bp.route("/EserciziScheda/<int:scheda_id>", methods=["GET"])
@login_required
def manage_eserciziScheda(scheda_id):

    eserciziScheda = (
        EserciziScheda.query
        .join(Tipoesercizi)
        .filter(EserciziScheda.scheda == scheda_id)
        .order_by(EserciziScheda.giorno, EserciziScheda.numero)
        .all()
    )
    utenti = User.query.all()
    # 👉 Raggruppa SOLO per giorno
    esercizi_per_giorno = {}

    for esercizio in eserciziScheda:
        giorno = esercizio.giorno

        if giorno not in esercizi_per_giorno:
            esercizi_per_giorno[giorno] = []

        esercizi_per_giorno[giorno].append(esercizio)

    return render_template(
        "esercizi_scheda.html",
        esercizi_per_giorno=esercizi_per_giorno,
        scheda_id=scheda_id ,utenti = utenti
    )

@bp.route("/add_esercizioScheda/<int:scheda_id>", methods=["GET", "POST"])
@login_required
def add_esercizioScheda(scheda_id):
    if request.method == "POST":
        # Ottieni i dati dal form
        esercizio_id = request.form.get("esercizio")
        ripetizioni = request.form.get("ripetizioni")
        carico = request.form.get("carico")
        numero = request.form.get("numero")
        isCompleta = request.form.get('isCompleta')
        if carico == '' :
            carico = 0

        recupero = request.form.get("recupero")
        serie = request.form.get("serie")
       
        note = request.form.get("note")
        giorno = request.form.get("giorno")

        
        nuovo_carico = 0
        
        nuove_ripetizioni = 0
       
        nuova_serie = 0
        # Crea un nuovo oggetto EserciziScheda
        esercizio = EserciziScheda(
            scheda=scheda_id,  # Usa il scheda_id passato nella URL
            esercizio=esercizio_id,
            ripetizioniStr =ripetizioni,
            carico=carico,
            recupero=recupero,
            serie=serie,
            nuovo_carico=nuovo_carico,
            nuove_ripetizioni=nuove_ripetizioni,
            nuova_serie=nuova_serie,
            note=note,
            giorno=giorno,
            numero=numero
        )

        # Aggiungi l'esercizio al database
        db.session.add(esercizio)
        db.session.commit()
        if isCompleta == False:
            return redirect(url_for("admin.manage_eserciziScheda", scheda_id=scheda_id))
        else :
            return redirect(url_for('admin.visualizza_scheda', scheda_id = scheda_id))
          # Reindirizza alla pagina della scheda

    # GET: Ottieni tutte le informazioni necessarie per il form (tipoesercizi)
    tipoesercizi = Tipoesercizi.query.order_by(Tipoesercizi.nome).all()

    return render_template("add_esercizio_scheda.html", tipoesercizi=tipoesercizi, scheda_id=scheda_id)

@bp.route('/tipoesercizi/modifica/<int:id>', methods=['GET', 'POST'])
def modifica_tipoesercizio(id):
    esercizio = Tipoesercizi.query.get_or_404(id)

    if request.method == 'POST':
        esercizio.nome = request.form['nome']
        esercizio.link = request.form['link']
        esercizio.tipo = request.form['tipo']

        db.session.commit()
        flash('Esercizio modificato con successo', 'success')
        return redirect(url_for('admin.gestione_tipoesercizi'))

    return render_template(
        'edit_tipoesercizio.html',
        esercizio=esercizio
    )


@bp.route('/appuntamenti')
def appuntamenti():
    appuntamenti = Appuntamenti.query.order_by(Appuntamenti.data.asc()).all()
    return render_template(
        'appuntamenti.html',
        appuntamenti=appuntamenti
    )


@bp.route("/appuntamenti/add/<int:user_id>", methods=["GET", "POST"])
@bp.route('/appuntamenti/add', methods=['GET', 'POST'])
def add_appuntamento(user_id = None):
    users = User.query.filter_by(is_admin = False, is_active = True).all()
    if user_id != None :
        selected_user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        data = datetime.strptime(
            request.form['data'],
            '%Y-%m-%dT%H:%M'
        )
        user_fromform = request.form.get("user_id")  # user_id sarà una stringa, quindi potresti volerlo convertire in int
        
        if user_fromform:
            user_fromform = int(user_fromform)
        tipologia = request.form['tipologia']
        nuovo = Appuntamenti(
            userid=user_fromform,
            data=data,
            tipologia = tipologia
        )
        db.session.add(nuovo)
        db.session.commit()

        flash('Appuntamento aggiunto con successo', 'success')
        return redirect(url_for('admin.appuntamenti'))

    return render_template('add_appuntamento.html', users = users)

@bp.route('/appuntamento/delete/<int:app_id>', methods=['POST'])
@login_required
def delete_appuntamento(app_id):
    if not current_user.is_admin and not current_user.is_worker:
        flash('Non puoi fare questa operazione!', 'error')
        return redirect(url_for('home.home'))
    appuntamento = Appuntamenti.query.get(app_id)
    if appuntamento:
       
            db.session.delete(appuntamento)
            db.session.commit()
            flash('Appuntamento eliminato con successo!', 'success')
    return redirect(url_for('admin.appuntamenti'))

@bp.route("/appuntamento/modifica/<int:app_id>", methods=["GET", "POST"])
@login_required
def edit_appuntamento(app_id):
    appuntamento = Appuntamenti.query.get(app_id)
    users = User.query.filter_by(is_admin = False, is_active = True).all()
    if request.method == 'POST':
        data = datetime.strptime(
            request.form['data'],
            '%Y-%m-%dT%H:%M'
        )
        user_fromform = request.form.get("user_id")  # user_id sarà una stringa, quindi potresti volerlo convertire in int
        
        if user_fromform:
            user_fromform = int(user_fromform)
        tipologia = request.form['tipologia']
        # Aggiorna 
       
        appuntamento.data = data
        appuntamento.userid = user_fromform
        appuntamento.tipologia = tipologia
        # Salva le modifiche
        db.session.commit()

        flash("Appuntamento aggiornato con successo", "success")
        return redirect(url_for("admin.appuntamenti"))

    # Restituisce il template con la scheda e gli utenti
    return render_template("edit_appuntamento.html", appuntamento=appuntamento, users=users)

@bp.route('/check')
def check():
    check = Check.query.order_by(Check.userid.asc(), Check.data_inserimento.asc() ).all()
    return render_template(
        'check.html',
        check=check
    )

@bp.route('/check/delete/<int:check_id>', methods=['POST'])
@login_required
def delete_check(check_id):
    check = Check.query.get(check_id)
    if check:
       
            db.session.delete(check)
            db.session.commit()
            flash('Check eliminato con successo!', 'success')
    return redirect(url_for('admin.appuntamenti'))

@bp.route("/check/<int:check_id>")
def view_single_check(check_id):
    check = Check.query.get_or_404(check_id)
    parametri = Parametri.query.first()  # o come li recuperi tu
    return render_template(
        "checkAnswers.html",
        titolo="Dettaglio Check",
        check=check,
        parametri=parametri
    )

@bp.route("/check/<int:check_id>/edit", methods=["GET", "POST"])
@login_required
def edit_check(check_id):
    check = Check.query.get_or_404(check_id)


    if request.method == "POST":
        check.risposta1 = request.form.get("risposta1")
        check.risposta2 = request.form.get("risposta2")
        check.risposta3 = request.form.get("risposta3")
        check.risposta4 = request.form.get("risposta4")
        check.risposta5 = request.form.get("risposta5")
        check.risposta6 = request.form.get("risposta6")
        check.risposta7 = request.form.get("risposta7")
        check.risposta8 = request.form.get("risposta8")
        check.risposta9 = request.form.get("risposta9")
        check.risposta10 = request.form.get("risposta10")
        check.rispostacheck = request.form.get("rispostacheck")
        check.note = request.form.get("note")

        db.session.commit()
        flash("Check aggiornato con successo ✅", "success")
        return redirect(url_for("admin.check"))

    parametri = Parametri.query.first()  # come già fai nella creazione
    return render_template("edit_check.html", check=check, parametri=parametri, titolo="Modifica Check")


@bp.route('/schede/delete_EsercizioScheda/<int:id>', methods=['POST'])
@login_required
def delete_EsercizioScheda(id):
    if not current_user.is_admin and not current_user.is_worker:
        flash('Non puoi fare questa operazione!', 'error')
        return redirect(url_for('home.home'))
    isCompleta = False
    eserciziScheda = EserciziScheda.query.get(id)
    Schedaid = eserciziScheda.scheda
    isCompleta = request.form.get('isCompleta')
    if eserciziScheda:
       
            db.session.delete(eserciziScheda)
            db.session.commit()
            flash('Esercizio eliminato con successo!', 'success')
    if isCompleta == False:
        return redirect(url_for('admin.manage_eserciziScheda', scheda_id = Schedaid))
    else : 
        return redirect(url_for('admin.visualizza_scheda', scheda_id = Schedaid))
    
@bp.route('/schede/get_schede/<int:user_id>')
@login_required
def get_schede(user_id):
    schede = Scheda.query.filter_by(userid=user_id).all()

    return jsonify([
        {"id": s.id, "titolo": s.titolo}
        for s in schede
    ])

@bp.route('/schede/copia_ajax', methods=['POST'])
@login_required
def copia_scheda_ajax():
    data = request.get_json()

    scheda_src_id = int(data.get("scheda_src_id"))
    scheda_dest_id = int(data.get("scheda_dest_id"))

    esercizi_src = EserciziScheda.query.filter_by(scheda=scheda_src_id).all()

    # opzionale: pulisci destinazione
    EserciziScheda.query.filter_by(scheda=scheda_dest_id).delete()

    for e in esercizi_src:
        nuovo = EserciziScheda(
            scheda = scheda_dest_id,
            esercizio = e.esercizio,
            ripetizioni = e.ripetizioni,
            ripetizioniStr = e.ripetizioniStr,
            carico = 0,
            recupero = e.recupero,
            serie = e.serie,
            nuovo_carico = 0,
            nuove_ripetizioni= 0,
            nuova_serie = 0,
            note = e.note,
            avanzamento = '',
            giorno = e.giorno,
            numero = e.numero
        )
        db.session.add(nuovo)

    db.session.commit()

    return jsonify({"message": "Scheda copiata con successo!"})

@bp.route('/modifica_esercizio/<int:id>', methods=['GET', 'POST'])
def modifica_esercizio(id):
    esercizio = EserciziScheda.query.get_or_404(id)
    tipoesercizi = Tipoesercizi.query.all()
    isCompleta = False
    if request.method == 'POST':
        try:
            esercizio.giorno = request.form.get('giorno')
            esercizio.numero = request.form.get('numero')
            esercizio.recupero = request.form.get('recupero')
            esercizio.serie = request.form.get('serie')
            esercizio.note = request.form.get('note')
            
            isCompleta = request.form.get('isCompleta')
            tipo_id = request.form.get('esercizio')
            if tipo_id != '':
                esercizio.esercizio = tipo_id

            db.session.commit()
            flash("Esercizio aggiornato con successo", "success")
            if isCompleta == False:
                return redirect(url_for('admin.manage_eserciziScheda', scheda_id = esercizio.scheda))
            else :
                return redirect(url_for('admin.visualizza_scheda', scheda_id = esercizio.scheda))

        except Exception as e:
            db.session.rollback()
            flash(f"Errore: {str(e)}", "error")

    return render_template(
        'edit_esercizio.html',
        esercizio=esercizio,
        tipoesercizi=tipoesercizi
    )

@bp.route("/scheda/<int:scheda_id>")
def visualizza_scheda(scheda_id):
    esercizi = EserciziScheda.query.filter_by(scheda=scheda_id).order_by(
        EserciziScheda.giorno, EserciziScheda.numero
    ).all()
    tipi_per_giorno = {}
    # Raggruppo per giorno
    esercizi_per_giorno = defaultdict(list)
    for e in esercizi:
        esercizi_per_giorno[e.giorno].append(e)
        
        if e.giorno not in tipi_per_giorno:
            tipi_per_giorno[e.giorno] = []

        if e.Tipoesercizi and e.Tipoesercizi.tipo:

            tipo = e.Tipoesercizi.tipo

            if tipo not in tipi_per_giorno[e.giorno]:
                tipi_per_giorno[e.giorno].append(tipo)

    tipi_per_giorno = {
        giorno: " - ".join(tipi)
        for giorno, tipi in tipi_per_giorno.items()
    }

    return render_template("admin_schedaCompleta.html", esercizi_per_giorno=esercizi_per_giorno, isCompleta = True, scheda_id=scheda_id, tipi_per_giorno=tipi_per_giorno )


@bp.route("/manuale/<int:user_id>")
def apri_manuale(user_id):
    user = User.query.get_or_404(user_id)
    manuale_filename = f"{user.username}_manuale.pdf"
    return render_template("view_manuale.html", filename=manuale_filename)


@bp.route("/alimentare/<int:user_id>")
def apri_alimentare(user_id):
    user = User.query.get_or_404(user_id)
    alimentare_filename = f"{user.username}_alimentare.pdf"
    return render_template("view_manuale.html", filename=alimentare_filename)

@bp.route("/integrazione/<int:user_id>")
def apri_integrazione(user_id):
    user = User.query.get_or_404(user_id)
    integrazione_filename = f"{user.username}_integrazione.pdf"
    return render_template("view_manuale.html", filename=integrazione_filename)

@bp.route('/aggiorna_ordine_esercizi', methods=['POST'])
@login_required
def aggiorna_ordine_esercizi():

    data = request.get_json()

    for item in data['ordine']:

        esercizio = EserciziScheda.query.get(item['id'])

        if esercizio:
            esercizio.numero = item['numero']

    db.session.commit()

    return jsonify({
        'success': True
    })