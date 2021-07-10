from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, jsonify
from flask_security import login_required, logout_user, current_user
from squeezy.models.acl import AccessControlList, AccessDirective, ACLDirective
from squeezy.service.squeezy import SqueezyService, SqueezyServiceACLInUseError
from squeezy.models.file import File
from json import loads
api_module = Blueprint('api', __name__)


@api_module.route("/api/v1/acl/get_all")
@login_required
def acl_get_all():
    response = {
        "status": "ok"
    }
    try:
        acls = [
            {
                "id": acl.id,
                "label": acl.label,
                "type": acl.type,
                "isFile": acl.is_file,
                "fileId": acl.file_id,
                "params": acl.parameters,
                "priority": acl.priority
            }
            for acl in AccessControlList.query.order_by(AccessControlList.priority).all()
        ]
        response["response"] = acls
    except Exception as e:
        response["status"] = "error"
        response["message"] = e.args[0]
    return jsonify(response)


@api_module.route("/api/v1/directive/get_all")
@login_required
def directive_get_all():
    response = {
        "status": "ok"
    }
    try:
        directives = [
            {
                "id": directive.id,
                "deny": directive.deny,
                "type": directive.type,
                "priority": directive.priority,
                "acls": [
                    {
                        "acldir_id": acldir.id,
                        "id": acldir.acl.id,
                        "label": acldir.acl.label,
                        "negated": acldir.negated
                    }
                    for acldir in directive.acls
                ]
            }
            for directive in AccessDirective.query.order_by(AccessDirective.priority).all()
        ]
        response["response"] = directives
    except Exception as e:
        response["status"] = "error"
        response["message"] = e.args[0]
    return jsonify(response)


@api_module.route("/api/v1/files/get_all")
@login_required
def files_get_all():
    response = {
        "status": "ok"
    }
    try:
        files = [{"id": file.id, "label": file.label}
                 for file in File.query.all()]
        response["response"] = files
    except Exception as e:
        response["status"] = "error"
        response["message"] = e.args[0]
    return jsonify(response)


@api_module.route("/api/v1/acl/update", methods=["POST"])
@login_required
def acl_update():
    response = {
        "status": "ok"
    }
    try:
        acl_data = loads(request.data)
        id = SqueezyService().update_acl(acl_data)
        response["message"] = f"updated id {id}"
        response["response"] = [{
            "id": id
        }]
    except Exception as e:
        response["status"] = "error"
        response["message"] = e.args[0]
    return jsonify(response)


@api_module.route("/api/v1/acl/delete", methods=["POST"])
@login_required
def acl_delete():
    response = {
        "status": "ok"
    }
    try:
        acl_data = loads(request.data)
        id = SqueezyService().delete_acl(acl_data)
        response["message"] = f"deleted id {id}"

    except Exception as e:
        response["status"] = "error"
        response["message"] = e.args[0]
    except SqueezyServiceACLInUseError as e:
        response["status"] = "error"
        response["message"] = e.args[0]

    return jsonify(response)


@api_module.route("/api/v1/directive/delete", methods=["POST"])
@login_required
def directive_delete():
    response = {
        "status": "ok"
    }
    try:
        acl_data = loads(request.data)
        id = SqueezyService().delete_directive(acl_data)
        response["message"] = f"deleted id {id}"

    except Exception as e:
        response["status"] = "error"
        response["message"] = e.args[0]
    return jsonify(response)


@api_module.route("/api/v1/directive/update", methods=["POST"])
@login_required
def directive_update():
    response = {
        "status": "ok"
    }
    try:
        directive_data = loads(request.data)
        directive = SqueezyService().update_directive(directive_data)
        response["message"] = f"updated id {directive.id}"
        response["response"] = [{
            "id": directive.id,
            "deny": directive.deny,
            "type": directive.type,
            "priority": directive.priority,
            "acls": [
                {
                    "acldir_id": acldir.id,
                    "id": acldir.acl.id,
                    "label": acldir.acl.label,
                    "negated": acldir.negated
                }
                for acldir in directive.acls
            ]
        }]
    except Exception as e:
        response["status"] = "error"
        response["message"] = e.args[0]
    return jsonify(response)
