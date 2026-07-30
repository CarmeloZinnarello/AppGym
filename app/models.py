from . import db
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import Enum
from datetime import date, datetime, timezone


class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    nome = db.Column(
        db.String(255),
        nullable=False,
        default='AdminNome'
    )

    cognome = db.Column(
        db.String(255),
        nullable=False,
        default='AdminCognome'
    )

    cf = db.Column(db.String(16), nullable=True)

    sesso = db.Column(
        Enum('M', 'F', 'Altro', name='sesso_enum'),
        nullable=True
    )

    is_admin = db.Column(db.Boolean, default=False)

    is_worker = db.Column(db.Boolean, default=False)

    is_active = db.Column(db.Boolean, default=True)

    # RELAZIONI

    schede = db.relationship(
        'Scheda',
        backref='user',
        lazy=True,
        cascade="all, delete-orphan"
    )

    appuntamenti = db.relationship(
        'Appuntamenti',
        backref='user',
        lazy=True,
        cascade="all, delete-orphan"
    )

    checks = db.relationship(
        'Check',
        backref='user',
        lazy=True,
        cascade="all, delete-orphan"
    )

    pagamenti = db.relationship(
        'Pagamenti',
        backref='user',
        lazy=True,
        cascade="all, delete-orphan"
    )

    consigli_alimentari = db.relationship(
        'ConsigliAlimentari',
        backref='user',
        lazy=True,
        cascade="all, delete-orphan"
    )

    storico_pesi = db.relationship(
        'StoricoPeso',
        backref='utente',
        lazy=True,
        cascade="all, delete-orphan",
        order_by="desc(StoricoPeso.data_inserimento)"
    )

class Pagamenti(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    userid = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    importo = db.Column(db.Float, nullable=True)

    data = db.Column(db.Date, nullable=False)

    prossima_scadenza = db.Column(
        db.Date,
        nullable=False
    )

    pagato = db.Column(db.Boolean, default=False)


class Check(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    userid = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    data_inserimento = db.Column(
        db.Date,
        nullable=False
    )

    note = db.Column(db.Text, nullable=True)

    risposta1 = db.Column(db.Text, nullable=True)
    risposta2 = db.Column(db.Text, nullable=True)
    risposta3 = db.Column(db.Text, nullable=True)
    risposta4 = db.Column(db.Text, nullable=True)
    risposta5 = db.Column(db.Text, nullable=True)
    risposta6 = db.Column(db.Text, nullable=True)
    risposta7 = db.Column(db.Text, nullable=True)
    risposta8 = db.Column(db.Text, nullable=True)
    risposta9 = db.Column(db.Text, nullable=True)
    risposta10 = db.Column(db.Text, nullable=True)

    rispostacheck = db.Column(db.Text, nullable=True)


class Appuntamenti(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    userid = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    data = db.Column(
        db.DateTime,
        nullable=False
    )

    tipologia = db.Column(
        Enum(
            'Appuntamento',
            'Scadenza',
            'Check',
            name='tipologia_enum',
            native_enum=False
        ),
        nullable=False,
        default='Appuntamento'
    )


class Parametri(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    banner = db.Column(db.Text, nullable=True)

    titolo = db.Column(
        db.String(255),
        nullable=True
    )

    sfondo = db.Column(
        db.String(255),
        nullable=True
    )

    sliderPaginaPrincipale = db.Column(
        db.Text,
        nullable=True
    )

    domanda1 = db.Column(db.Text, nullable=True)
    domanda2 = db.Column(db.Text, nullable=True)
    domanda3 = db.Column(db.Text, nullable=True)
    domanda4 = db.Column(db.Text, nullable=True)
    domanda5 = db.Column(db.Text, nullable=True)
    domanda6 = db.Column(db.Text, nullable=True)
    domanda7 = db.Column(db.Text, nullable=True)
    domanda8 = db.Column(db.Text, nullable=True)
    domanda9 = db.Column(db.Text, nullable=True)
    domanda10 = db.Column(db.Text, nullable=True)


class Tipoesercizi(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(
        db.String(255),
        nullable=True
    )

    link = db.Column(
        db.String(255),
        nullable=True
    )

    tipo = db.Column(
        Enum(
            'Gambe',
            'Petto',
            'Schiena',
            'Spalle',
            'Braccia',
            'Core',
            'Stretching',
            name='tipo_esercizio_enum'
        ),
        nullable=True
    )


class Scheda(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    userid = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    data_inizio = db.Column(
        db.Date,
        nullable=False
    )

    data_fine = db.Column(
        db.Date,
        nullable=True
    )

    titolo = db.Column(
        db.String(255),
        nullable=True
    )

    numero = db.Column(
        db.Integer,
        nullable=False
    )
    is_active = db.Column(db.Boolean, default=True)

class EserciziScheda(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    scheda = db.Column(
        db.Integer,
        db.ForeignKey('scheda.id'),
        nullable=False
    )

    esercizio = db.Column(
        db.Integer,
        db.ForeignKey('tipoesercizi.id'),
        nullable=False
    )

    ripetizioni = db.Column(
        db.Integer,
        nullable=True
    )

    ripetizioniStr = db.Column(
        db.Text,
        nullable=True
    )

    carico = db.Column(
        db.Float,
        nullable=True
    )

    recupero = db.Column(
        db.Text,
        nullable=True
    )

    serie = db.Column(
        db.Integer,
        nullable=True
    )

    nuovo_carico = db.Column(
        db.Float,
        nullable=True
    )

    nuove_ripetizioni = db.Column(
        db.Integer,
        nullable=True
    )

    nuova_serie = db.Column(
        db.Integer,
        nullable=True
    )

    note = db.Column(
        db.Text,
        nullable=True
    )

    avanzamento = db.Column(
        db.Text,
        nullable=True
    )

    giorno = db.Column(
        db.Integer,
        nullable=False
    )

    numero = db.Column(
        db.Integer,
        nullable=True
    )

    noteUtente = db.Column(
        db.Text,
        nullable=True
    )

    Tipoesercizi = db.relationship(
        'Tipoesercizi',
        backref='esercizi_scheda',
        lazy=True
    )

    Scheda = db.relationship(
        'Scheda',
        backref=db.backref(
            'esercizi_scheda',
            cascade="all, delete-orphan",
            lazy=True
        )
    )


class ConsigliAlimentari(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    userid = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    link = db.Column(
        db.String(255),
        nullable=True
    )


class EserciziSchedaProgress(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    scheda = db.Column(
        db.Integer,
        db.ForeignKey('scheda.id'),
        nullable=False
    )

    esercizio = db.Column(
        db.Integer,
        db.ForeignKey('tipoesercizi.id'),
        nullable=False
    )

    ripetizioni = db.Column(
        db.Integer,
        nullable=True
    )

    carico = db.Column(
        db.Float,
        nullable=True
    )

    recupero = db.Column(
        db.Integer,
        nullable=False
    )

    serie = db.Column(
        db.Integer,
        nullable=False
    )

    nuovo_carico = db.Column(
        db.Float,
        nullable=True
    )

    nuove_ripetizioni = db.Column(
        db.Integer,
        nullable=True
    )

    nuova_serie = db.Column(
        db.Integer,
        nullable=True
    )

    note = db.Column(
        db.Text,
        nullable=True
    )

    avanzamento = db.Column(
        db.Text,
        nullable=True
    )

    giorno = db.Column(
        db.Integer,
        nullable=False
    )

    data = db.Column(
        db.Date,
        nullable=False
    )

    numero = db.Column(
        db.Integer,
        nullable=True
    )

    Tipoesercizi = db.relationship(
        'Tipoesercizi',
        backref='esercizi_schedaProg',
        lazy=True
    )

    Scheda = db.relationship(
        'Scheda',
        backref=db.backref(
            'esercizi_schedaProg',
            cascade="all, delete-orphan",
            lazy=True
        )
    )

class StoricoPeso(db.Model):
    __tablename__ = 'storico_peso'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    peso = db.Column(
        db.Float,
        nullable=False
    )

    data_inserimento = db.Column(
    db.DateTime,
    nullable=False,
    default=lambda: datetime.now(timezone.utc)
    )