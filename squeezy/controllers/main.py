from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask_security import login_required, logout_user, current_user
from squeezy.models.user import User

main_module = Blueprint('main', __name__)

@main_module.route("/")
@login_required
def root():
    return render_template("index.html.j2", title="Squeezy", user=current_user)

@main_module.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.root'))


