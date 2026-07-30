from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, current_user
from werkzeug.security import check_password_hash
from ..models import User, Parametri
from sqlalchemy import func
bp = Blueprint('home', __name__)

@bp.route('/', methods=['GET', 'POST'])
def home():
    titolo = Parametri.query.first().titolo if Parametri.query.first() else "WebFit"

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter(func.lower(User.username) == username.lower()).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.is_admin or  user.is_worker:
                accessgestione = True
            else:
                accessgestione = False      
            return redirect(url_for('admin.dashboard')) if accessgestione else redirect(url_for('user.dashboard'))
        else:
            flash("Credenziali errate", "error")

    return render_template('home.html', titolo=titolo)