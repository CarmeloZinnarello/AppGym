from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from ..models import db, User, Parametri, Scheda, EserciziScheda, Tipoesercizi, Check, Appuntamenti, EserciziSchedaProgress, StoricoPeso
from datetime import datetime, timedelta
from sqlalchemy import or_
from datetime import date
from flask import send_from_directory
from collections import defaultdict
import os
bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/')
@login_required
def dashboard():
    parametri = Parametri.query.first()
    user = current_user
    Appuntamento = Appuntamenti.query.filter(Appuntamenti.data >= date.today(), Appuntamenti.userid == current_user.id, Appuntamenti.tipologia == 'Appuntamento').order_by(Appuntamenti.data).first()
    Check = Appuntamenti.query.filter(Appuntamenti.data >= date.today(), Appuntamenti.userid == current_user.id, Appuntamenti.tipologia == 'Check').order_by(Appuntamenti.data).first()
    return render_template('user.html', parametri=parametri, user = user, Appuntamento = Appuntamento, Check = Check)

@bp.route("/Schede", methods=["GET"])
@bp.route("/Schede/<int:user_id>", methods=["GET"])
@login_required
def manage_schede():
    user_id = current_user.id

    query = Scheda.query
    if user_id:
        query = query.filter(Scheda.userid == user_id, Scheda.is_active == True)

    schede = query.order_by(Scheda.userid.asc(), Scheda.numero.asc(),Scheda.data_fine.asc()).all()

    return render_template("view_schede.html", schede=schede, user_id=user_id)   

#@bp.route("/EserciziScheda/<int:scheda_id>", methods=["GET"])
#@login_required
#def manage_eserciziScheda(scheda_id):
#    # Query ordinata per giorno e numero
#    eserciziScheda = (
#        EserciziScheda.query
#        .filter(EserciziScheda.scheda == scheda_id)
#        .order_by(EserciziScheda.giorno, EserciziScheda.numero)
#        .all()
#    )
#
#    # Raggruppa SOLO per giorno
#    esercizi_per_giorno = {}
#    for esercizio in eserciziScheda:
#        giorno = esercizio.giorno
#
#        if giorno not in esercizi_per_giorno:
#            esercizi_per_giorno[giorno] = []
#
#        esercizi_per_giorno[giorno].append(esercizio)
#
#    return render_template(
#        "esercizi_scheda_user.html",
#        esercizi_per_giorno=esercizi_per_giorno,
#        scheda_id=scheda_id
#    )

@bp.route("/EserciziScheda/<int:scheda_id>", methods=["GET"])
@login_required
def manage_eserciziScheda(scheda_id):

    eserciziScheda = (
        EserciziScheda.query
        .filter(EserciziScheda.scheda == scheda_id)
        .order_by(EserciziScheda.giorno, EserciziScheda.numero)
        .all()
    )

    # giorno -> numero -> lista esercizi
    esercizi_per_giorno = {}
    tipi_per_giorno ={}
    for esercizio in eserciziScheda:
        giorno = esercizio.giorno
        numero = esercizio.numero

        # crea giorno
        if giorno not in esercizi_per_giorno:
            esercizi_per_giorno[giorno] = {}

        # crea gruppo numero
        if numero not in esercizi_per_giorno[giorno]:
            esercizi_per_giorno[giorno][numero] = []

        # aggiungi esercizio
        esercizi_per_giorno[giorno][numero].append(esercizio)

         # Tipologie del giorno
        if giorno not in tipi_per_giorno:
            tipi_per_giorno[giorno] = []

        if esercizio.Tipoesercizi and esercizio.Tipoesercizi.tipo:

            tipo = esercizio.Tipoesercizi.tipo

            if tipo not in tipi_per_giorno[giorno]:
                tipi_per_giorno[giorno].append(tipo)

    tipi_per_giorno = {
    giorno: " - ".join(tipi)
    for giorno, tipi in tipi_per_giorno.items()
}
    return render_template(
        "esercizi_scheda_user.html",
        esercizi_per_giorno=esercizi_per_giorno,
        tipi_per_giorno=tipi_per_giorno,
        scheda_id=scheda_id
    )

@bp.route('/check', methods=['GET', 'POST'])
@login_required
def check():
    parametri = Parametri.query.first()

    if request.method == 'POST':
        check = Check(
            userid=current_user.id,
            data_inserimento=date.today(),
            note=request.form.get('note'),
            risposta1=request.form.get('risposta1'),
            risposta2=request.form.get('risposta2'),
            risposta3=request.form.get('risposta3'),
            risposta4=request.form.get('risposta4'),
            risposta5=request.form.get('risposta5'),
            risposta6=request.form.get('risposta6'),
            risposta7=request.form.get('risposta7'),
            risposta8=request.form.get('risposta8'),
            risposta9=request.form.get('risposta9'),
            risposta10=request.form.get('risposta10'),
        )
        db.session.add(check)
        db.session.commit()
        return redirect(url_for('home.home'))

    return render_template(
        'check.html',
        parametri=parametri,
        titolo='Questionario'
    )


@bp.route("/salva_progressi", methods=["POST"])
def salva_progressi():
    esercizi = []
    for key, value in request.form.items():
        if key.startswith("esercizio_"):
            esercizio_id = int(key.split("_")[1])
            campo = key.split("_")[2]
            nuovo_avanzamentno = ''
            noteUtente = ''
            esercizio = EserciziScheda.query.get(esercizio_id)
            noteUtente = esercizio.noteUtente
            if not esercizio:
                continue

            if campo == "avanzamento" :
                nuovo_avanzamentno = value if value else ""
            if campo == "noteUtente" :
                noteUtente = value if value else ""   
                esercizio.noteUtente = noteUtente
            if campo == "carico":
                nuovo_carico = float(value.replace(",", ".")) if value else None
            elif campo == "ripetizioni" :     
                nuove_ripetizioni = int(value) if value else None
            elif campo == "serie":
                nuova_serie = int(value) if value else None
            
            if campo == "avanzamento" and nuovo_avanzamentno != "" and esercizio.avanzamento != nuovo_avanzamentno:
                esercizio.avanzamento = nuovo_avanzamentno
                if not esercizio_id in esercizi :
                    esercizi.append(esercizio_id)
            if campo == "carico" and nuovo_carico != None and esercizio.nuovo_carico != nuovo_carico :
                esercizio.nuovo_carico = nuovo_carico
                if not esercizio_id in esercizi :
                    esercizi.append(esercizio_id)
            elif campo == "ripetizioni" and nuove_ripetizioni != None and esercizio.nuove_ripetizioni != nuove_ripetizioni:
                esercizio.nuove_ripetizioni = nuove_ripetizioni
                if not esercizio_id in esercizi :
                    esercizi.append(esercizio_id)
            elif campo == "serie" and nuova_serie != None and esercizio.nuova_serie != nuova_serie:
                esercizio.nuova_serie = nuova_serie
                if not esercizio_id in esercizi :
                    esercizi.append(esercizio_id)
              
           
               
   
    db.session.commit()

    for eser in esercizi :
        esercizio = EserciziScheda.query.get(eser)
        prog = EserciziSchedaProgress(
            scheda = esercizio.scheda,
            esercizio = esercizio.esercizio,
            ripetizioni = esercizio.ripetizioni,
            carico = esercizio.carico,
            recupero = esercizio.recupero,
            serie = esercizio.serie,
            nuovo_carico = esercizio.nuovo_carico,
            nuove_ripetizioni = esercizio.nuove_ripetizioni,
            nuova_serie= esercizio.nuova_serie,
            note = esercizio.note,
            giorno = esercizio.giorno,
            avanzamento = esercizio.avanzamento,
            numero = esercizio.numero,
            data = date.today()
        )

        esercizio.noteUtente = noteUtente
        db.session.add(prog)
        db.session.commit()
    flash("Progressi salvati 💪")
    return redirect(request.referrer)

@bp.route('/appuntamenti')
def appuntamenti():
    appuntamenti = Appuntamenti.query.filter(Appuntamenti.userid == current_user.id).order_by(Appuntamenti.data.asc()).all()
    return render_template(
        'appuntamenti_user.html',
        appuntamenti=appuntamenti
    )

@bp.route('/viewcheck')
def viewcheck():
    check = Check.query.filter(Check.userid == current_user.id).order_by( Check.data_inserimento.asc() ).all()
    return render_template(
        'check_user.html',
        check=check
    )

@bp.route("/send_check", methods=['GET', 'POST'])
def send_check():
    parametri = Parametri.query.first()
    if request.method == 'POST':
        check = Check(
            userid=current_user.id,
            data_inserimento=date.today(),
            note=request.form.get('note'),
            risposta1=request.form.get('risposta1'),
            risposta2=request.form.get('risposta2'),
            risposta3=request.form.get('risposta3'),
            risposta4=request.form.get('risposta4'),
            risposta5=request.form.get('risposta5'),
            risposta6=request.form.get('risposta6'),
            risposta7=request.form.get('risposta7'),
            risposta8=request.form.get('risposta8'),
            risposta9=request.form.get('risposta9'),
            risposta10=request.form.get('risposta10'),
        )
        db.session.add(check)
        db.session.commit()
    return render_template("send_check.html", parametri=parametri)


@bp.route("/check/<int:check_id>")
def view_single_check(check_id):
    check = Check.query.get_or_404(check_id)
    parametri = Parametri.query.first()  # o come li recuperi tu
    return render_template(
        "checkAnswers_user.html",
        titolo="Dettaglio Check",
        check=check,
        parametri=parametri
    )

@bp.route('/check/delete/<int:check_id>', methods=['POST'])
@login_required
def delete_check(check_id):
    check = Check.query.get(check_id)
    if check:
       
            db.session.delete(check)
            db.session.commit()
            flash('Check eliminato con successo!', 'success')
    return redirect(url_for('user.viewcheck'))

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
        check.note = request.form.get("note")

        db.session.commit()
        flash("Check aggiornato con successo ✅", "success")
        return redirect(url_for("user.viewcheck"))

    parametri = Parametri.query.first()  # come già fai nella creazione
    return render_template("edit_check_user.html", check=check, parametri=parametri, titolo="Modifica Check")


@bp.route("/ProgressiScheda/<int:scheda_id>", methods=["GET"])
@login_required
def progressiScheda(scheda_id):
    eserciziScheda = (
    EserciziSchedaProgress.query
    .join(Tipoesercizi)  # Fai il join con la tabella Tipoesercizi
    .filter(EserciziSchedaProgress.scheda == scheda_id)  # Usa EserciziScheda per il filtro
    .order_by(EserciziSchedaProgress.data)  # Ordina per giorno e tipo
    .group_by(EserciziSchedaProgress.data)
    .all())
    # Passa i dati raggruppati al template
    return render_template("progressiScheda.html", eserciziScheda=eserciziScheda, scheda_id = scheda_id)

@bp.route("/EserciziSchedaProgView/<data>/<int:schedaid>", methods=["GET"])
@login_required
def progr_eserciziScheda(data, schedaid):

    eserciziScheda = (
        EserciziSchedaProgress.query
        .filter(
            EserciziSchedaProgress.data == data,
            EserciziSchedaProgress.scheda == schedaid
        )
        .order_by(
            EserciziSchedaProgress.giorno,
            EserciziSchedaProgress.numero
        )
        .all()
    )

    esercizi_per_giorno = {}

    for esercizio in eserciziScheda:
        giorno = esercizio.giorno

        if giorno not in esercizi_per_giorno:
            esercizi_per_giorno[giorno] = []

        esercizi_per_giorno[giorno].append(esercizio)

    scheda_id = eserciziScheda[0].scheda if eserciziScheda else None

    return render_template(
        "esercizi_scheda_user_progr.html",
        esercizi_per_giorno=esercizi_per_giorno,
        scheda_id=scheda_id
    )

@bp.route("/manuale/")
def apri_manuale():
    manuale_filename = f"{current_user.username}_manuale.pdf"
    version = datetime.now().timestamp()
    return render_template("view_manuale.html", filename=manuale_filename, version = version)

@bp.route("/alimentare/")
def apri_alimentare():
    alimentare_filename = f"{current_user.username}_alimentare.pdf"
    version = datetime.now().timestamp()
    return render_template("view_manuale.html", filename=alimentare_filename, version = version)

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

    return render_template("schedaCompleta.html", esercizi_per_giorno=esercizi_per_giorno,  tipi_per_giorno=tipi_per_giorno)

@bp.route("/graficoScheda/<int:scheda_id>")
@login_required
def grafico_scheda(scheda_id):
    esercizi = (
        EserciziSchedaProgress.query
        .join(Tipoesercizi)
        .filter(EserciziSchedaProgress.scheda == scheda_id)
        .order_by(EserciziSchedaProgress.data)
        .all()
    )

    import re
    from collections import defaultdict

    grafico = defaultdict(list)

    for e in esercizi:
        nome = e.Tipoesercizi.nome

        # Estrai serie dal campo note
        serie = re.findall(r"Serie (\d+): ([\d\.]+)kg x (\d+)", e.avanzamento, re.IGNORECASE)

        for num_serie, kg, reps in serie:
            kg = float(kg)
            reps = int(reps)

            if kg == 0 or reps == 0:
                continue

            grafico[nome].append({
                "label": f"{e.data.strftime('%d/%m')} S{num_serie}",
                "kg": kg,
                "reps": reps,
                "serie": int(num_serie)
            })

    return render_template(
        "graficoScheda.html",
        grafico=grafico,
        scheda_id=scheda_id
    )

@bp.route("/integrazione/")
def apri_integrazione():
    integrazione_filename = f"{current_user.username}_integrazione.pdf"
    version = datetime.now().timestamp()
    
    return render_template("view_manuale.html", filename=integrazione_filename, version = version)

@bp.route('/peso', methods=['GET', 'POST'])
@login_required
def peso():

    if request.method == 'POST':

        peso = request.form.get('peso')

        nuovo_peso = StoricoPeso(
            user_id=current_user.id,
            peso=float(peso)
        )

        db.session.add(nuovo_peso)
        db.session.commit()

        return redirect(url_for('user.peso'))

    storico_pesi = StoricoPeso.query\
        .filter_by(user_id=current_user.id)\
        .order_by(StoricoPeso.data_inserimento.desc())\
        .all()

    return render_template(
        'storico_peso.html',
        storico_pesi=storico_pesi
    )

@bp.route('/grafico-peso/<int:user_id>')
@login_required
def grafico_peso(user_id):

    limite = request.args.get('limite', 10, type=int)

    if limite < 1:
        limite = 1

    query = (StoricoPeso.query
             .filter_by(user_id=user_id)
             .order_by(StoricoPeso.data_inserimento.desc()))

    pesi = query.limit(limite).all()

    pesi.reverse()

    labels = [
        p.data_inserimento.strftime('%d/%m/%Y')
        for p in pesi
    ]

    valori = [
        p.peso
        for p in pesi
    ]

    media = round(sum(valori) / len(valori), 2) if valori else 0

    ultimo_peso = valori[-1] if valori else 0

    return render_template(
        'grafico_peso.html',
        labels=labels,
        valori=valori,
        media=media,
        ultimo_peso=ultimo_peso,
        limite=limite,
        user_id=user_id
    )

@bp.route('/peso/elimina/<int:peso_id>', methods=['POST'])
@login_required
def elimina_peso(peso_id):

    peso = StoricoPeso.query.get_or_404(peso_id)

    db.session.delete(peso)

    db.session.commit()

    flash('Peso eliminato')

    return redirect(url_for('user.peso'))

@bp.route('/peso/modifica/<int:peso_id>', methods=['GET', 'POST'])
@login_required
def modifica_peso(peso_id):

    peso = StoricoPeso.query.get_or_404(peso_id)

    if request.method == 'POST':

        peso.peso = float(request.form['peso'])
        peso.data_inserimento = datetime.strptime(
            request.form['data_inserimento'],
            '%Y-%m-%dT%H:%M'
        )

        db.session.commit()

        flash('Peso aggiornato')

        return redirect(url_for('user.peso'))

    return render_template(
        'modifica_peso.html',
        peso=peso
    )