import logging
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, jsonify
from json import dumps
from flask_security import login_required, logout_user, current_user
from squeezy.forms.settings import SettingsForm
from squeezy.forms.file import FileForm
from squeezy.models.settings import Settings
from squeezy.models.acl import AccessControlList
from squeezy.service.basic_settings import BasicSettingsService
from squeezy.service.squeezy import SqueezyService, SqueezyServiceFileFormatError, SqueezyServiceFileInUseError, SqueezySquidReconfigureError
from squeezy.models.file import File
from squeezy.helpers.acl_types import ACL_TYPES
from squeezy.helpers.directive_types import DIRECTIVE_TYPES
main_module = Blueprint('main', __name__)


@main_module.route("/")
@login_required
def root():
    return render_template("index.html.j2", user=current_user)

@main_module.route("/logs")
@login_required
def logs():
    return render_template("logs.html.j2", user=current_user)

@main_module.route("/users")
@login_required
def users():
    return render_template("users.html.j2", user=current_user)

@main_module.route("/logout", methods=["POST"])
@login_required
def logout():
    logging.info(f"About to log out user {current_user.email}")
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
            logging.info(f"handle_file_upload: {form.label.data} / {form.file.data.filename} / {form.file.data.content_length} / {form.file.data.content_type} ")
            SqueezyService().handle_file_upload(form)
        except SqueezyServiceFileFormatError as e:
            flash(f"Text file expected, got: {form.file.data.content_type}")
            logging.error(f"FileFormatError for handle_file_upload: {form.label.data} / {form.file.data.filename} / {form.file.data.content_length} / {form.file.data.content_type}")
        except Exception as e:
            flash(f"Unknown Error: {e.args[0]}")
        return redirect(url_for('main.files'))
    return render_template("files.html.j2", user=current_user, form=form, files=files)


@main_module.route("/files/<id>", methods=["GET", "POST"])
@login_required
def file(id: int):
    try:
        file = File.query.filter_by(id=id).first()
        content = SqueezyService().handle_file_read(file)
    except Exception as e:
        flash(f"Unhandled exception: {e.args}")
        logging.error(f"Error reading file: {e.args}")
        return redirect(url_for("main.root"))
    return render_template("file.html.j2", user=current_user, file=file, content=content)


@main_module.route("/files/delete", methods=["POST"])
@login_required
def file_delete():
    try:
        id = request.args.get("id")
        file = File.query.filter_by(id=id).first()
        SqueezyService().handle_file_delete(file)
    except SqueezyServiceFileInUseError as e:
        flash(f"Unhandled exception: {e.args}")
        return redirect(url_for("main.files"))
    except Exception as e:
        flash(f"Unhandled exception: {e.args}")
        return redirect(url_for("main.root"))
    return redirect(url_for('main.files'))


@main_module.route("/acls", methods=["GET", "POST"])
@login_required
def acls():
    return render_template("acls.html.j2", user=current_user, types=dumps(ACL_TYPES).replace("\"", "\\\""))


@main_module.route("/directives", methods=["GET"])
@login_required
def access_directives():
    return render_template("directives.html.j2", user=current_user, types=dumps(DIRECTIVE_TYPES).replace("\"", "\\\""))

@main_module.route("/apply", methods=["POST"])
@login_required
def apply_config():
    try:
        SqueezyService().apply_config()
    except Exception as e:
        flash(f"Unhandled exception: {e.args}")
        return redirect(url_for("main.root"))
    return redirect(url_for("main.get_config"))

@main_module.route("/config", methods=["GET"])
@login_required
def get_config():
    try:
        content = SqueezyService().get_config()
    except Exception as e:
        flash(f"Unhandled exception: {e.args}")
        return redirect(url_for("main.root"))
    return render_template("config.html.j2", user=current_user, content=content)

@main_module.route("/reconfigure", methods=["POST"])
@login_required
def reconfigure_squid():
    try:
        SqueezyService().reload_service()
    except SqueezySquidReconfigureError as e:
        flash(e.args[0])
        return redirect(url_for("main.get_config"))
    flash("Reload successeful!")
    return redirect(url_for("main.get_config"))