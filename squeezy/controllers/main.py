from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, jsonify
from json import dumps
from flask_security import login_required, logout_user, current_user
from squeezy.forms.settings import SettingsForm
from squeezy.forms.file import FileForm
from squeezy.models.settings import Settings
from squeezy.models.acl import AccessControlList
from squeezy.service.basic_settings import BasicSettingsService
from squeezy.service.squeezy import SqueezyService, SqueezyServiceFileFormatError
from squeezy.models.file import File
from squeezy.helpers.acl_types import ACL_TYPES
main_module = Blueprint('main', __name__)


@main_module.route("/")
@login_required
def root():
    return render_template("index.html.j2", user=current_user)


@main_module.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.root'))

@main_module.route("/basic", methods=["GET", "POST"])
@login_required
def basic_settings():
    settings = dict([(setting.key, setting.value) for setting in Settings.query.all()])
    form = SettingsForm(data=settings)
    if form.validate_on_submit():
        try:
            BasicSettingsService().updateSettings(form)
        except Exception as e:
            flash(f"Unknown Error: {e.args[0]}")
        return redirect(url_for('main.basic_settings'))
    return render_template("basic-settings.html.j2", user=current_user, form=form)


@main_module.route("/files", methods=["GET", "POST"])
@login_required
def files():
    form = FileForm()
    files = File.query.all()
    if form.validate_on_submit():
        try:
            SqueezyService().handle_file_upload(form)
        except SqueezyServiceFileFormatError as e:
            flash(f"Text file expected, got: {form.file.data.content_type}")
        except Exception as e:
            flash(f"Unknown Error: {e.args[0]}")
        return redirect(url_for('main.files'))
    return render_template("files.html.j2", user=current_user, form=form, files=files)


@main_module.route("/files/<id>", methods=["GET", "POST"])
@login_required
def file(id: int):
    file = File.query.filter_by(id=id).first()
    content = SqueezyService().handle_file_read(file)
    return render_template("file.html.j2", user=current_user, file=file, content=content)


@main_module.route("/files/delete", methods=["POST"])
@login_required
def file_delete():
    id = request.args.get("id")
    file = File.query.filter_by(id=id).first()
    SqueezyService().handle_file_delete(file)
    return redirect(url_for('main.files'))


@main_module.route("/acls", methods=["GET", "POST"])
@login_required
def acls():
    return render_template("acls.html.j2", user=current_user, types=dumps(ACL_TYPES).replace("\"", "\\\""))