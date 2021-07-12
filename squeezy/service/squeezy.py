import logging
from flask import g
from squeezy.models.acl import AccessControlList, AccessDirective, ACLDirective
from squeezy.forms.file import FileForm
from squeezy.models.file import File
from werkzeug.utils import secure_filename
from hashlib import sha256
from datetime import datetime
from config import ENVIRONMENT
from squeezy.helpers.acl_types import ACL_TYPES
from squeezy.helpers.directive_types import DIRECTIVE_TYPES
from database import db
from pathlib import Path
from subprocess import CompletedProcess, run
import os


class SqueezyServiceFileFormatError(Exception):
    pass

class SqueezyServiceFileInUseError(Exception):
    pass

class SqueezyServiceACLInUseError(Exception):
    pass

class SqueezySquidReconfigureError(Exception):
    pass

class SqueezyService:
    def handle_file_upload(self, form: FileForm):
        data = form.file.data
        if not data.content_type.startswith("text/"):
            raise SqueezyServiceFileFormatError("Plain Text files only")
        filename = secure_filename(data.filename)
        file_db = File()
        on_disk_name = sha256(
            bytes(filename + str(datetime.now()), encoding="utf-8")).hexdigest()
        file_db.label = form.label.data
        file_db.original_filename = filename

        file_db.filepath = f"file_{on_disk_name}"

        storage_path = ENVIRONMENT.get("SQUEEZY_FILE_STORAGE_PATH")
        filepath = os.path.join(ENVIRONMENT.get(
            "INSTANCE_PATH"), storage_path, file_db.filepath)
        normalized_path = Path(filepath)
        logging.debug(f"attempting to save to {normalized_path.absolute()}")
        with open(normalized_path.absolute(), "w+b") as f:
            data.save(f)
            f.seek(0)
            file_db.sha256 = sha256(f.read()).hexdigest()
        db.session.add(file_db)
        db.session.commit()

    def handle_file_read(self, file: File):
        storage_path = ENVIRONMENT.get("SQUEEZY_FILE_STORAGE_PATH")
        path = os.path.join(ENVIRONMENT.get(
            "INSTANCE_PATH"), storage_path, file.filepath)
        logging.info(f"open() called for {path}")
        with open(Path(path).absolute(), "rt", encoding="utf-8") as f:
            return f.read()

    def handle_file_delete(self, file: File):
        logging.debug(f"handle_file_delete called for {file.label}")
        if AccessControlList.query.filter_by(file_id=file.id).first():
            logging.warning(f"File is currently in use, unable to remove {file.original_filename} / {file.label}")
            raise SqueezyServiceFileInUseError(f"{file.original_filename} is in use by an ACL. Remove all references to this file before before proceeding")

        storage_path = ENVIRONMENT.get("SQUEEZY_FILE_STORAGE_PATH")
        path = os.path.join(ENVIRONMENT.get(
            "INSTANCE_PATH"), storage_path, file.filepath)
        logging.debug(f"attempting to delete {path}")
        os.unlink(path)
        db.session.delete(file)
        db.session.commit()

    def update_acl(self, acl_data: dict):
        logging.debug(f"update_acl called: {acl_data}")
        id = acl_data["id"]
        if id != -1:
            acl = AccessControlList.query.filter_by(id=id).first()
        else:
            acl = AccessControlList()

        if not acl:
            raise Exception("Wrong ACL id")

        if acl_data["isFile"]:
            acl.is_file = True
            acl.file_id = acl_data["fileId"]
            acl.parameters = None
        else:
            acl.is_file = False
            acl.parameters = acl_data["params"]
            acl.file_id = None

        acl.label = acl_data["label"]
        acl.priority = acl_data["priority"]
        acl.type = acl_data["type"]
        db.session.add(acl)
        db.session.commit()
        logging.info("New ACL has been added to the ACL table")
        return acl.id

    def delete_acl(self, acl_data: dict):
        logging.debug(f"delete_acl called: {acl_data}")
        id = acl_data["id"]
        if id != -1:
            acl = AccessControlList.query.filter_by(id=id).first()
        else:
            raise Exception("No id provided")

        if not acl:
            raise Exception("ACL does not exist")

        if ACLDirective.query.filter_by(acl=acl).first():
            logging.error(f"Attempt to remove an in-use ACL from database: {acl.id}")
            raise SqueezyServiceACLInUseError("ACL is in use by a Directive. Please remove all references to this ACL before deleting")

        db.session.delete(acl)
        db.session.commit()

        return id

    def delete_directive(self, directive_data: dict):
        logging.debug(f"delete_directive called: {directive_data}")
        id = directive_data["id"]
        directive: AccessDirective = AccessDirective.query.filter_by(
            id=id).first()

        if not directive:
            logging.error(f"delete_directive: Non existing directive was requested: {directive_data}")
            raise Exception("Directive does not exist")

        for acldir in directive.acls:
            db.session.delete(acldir)

        db.session.delete(directive)
        db.session.commit()
        logging.info(f"delete_directive: Directive delete finished for directive id {id}")
        return id

    def update_directive(self, directive_data: dict):
        logging.debug(f"update_directive called: {directive_data}")
        id = directive_data["id"]
        if id != -1:
            directive = AccessDirective.query.filter_by(id=id).first()
        else:
            directive = AccessDirective()

        if not directive:
            raise Exception("Wrong Directive id")

        directive.type = directive_data["type"]
        directive.priority = directive_data["priority"]
        directive.deny = directive_data["deny"]
        oldAcls = list(directive.acls)

        existingAcls = [(ACLDirective.query.filter_by(id=acldata["acldir_id"]).first(
        ), acldata) for acldata in directive_data["acls"] if acldata["acldir_id"] != -1]
        for acldir, acldata in existingAcls:
            acl = AccessControlList.query.filter_by(id=acldata["id"]).first()
            acldir.negated = acldata["negated"]
            acldir.acl = acl

        newAcls = [acldata for acldata in directive_data["acls"]
                   if acldata["acldir_id"] == -1 and acldata["id"] != -1]
        for newAcl in newAcls:
            aclDirective = ACLDirective()
            acl = AccessControlList.query.filter_by(id=newAcl["id"]).first()
            if not acl:
                logging.error(f"update_directive: Directive Update data contains a non-existent acl: {newAcl}")
                raise Exception("Non-existing ACL provided", newAcl)

            aclDirective.acl = acl
            aclDirective.directive = directive
            aclDirective.negated = newAcl["negated"]
            db.session.add(aclDirective)

        removedAcls = [
            aclToRemove for aclToRemove in oldAcls if aclToRemove not in existingAcls[0]]
        for removedAcl in removedAcls:
            db.session.delete(removedAcl)


        db.session.add(directive)
        db.session.commit()
        logging.info(f"update_directive: Directive create / update finished for directive id {directive.id}")
        return directive

    def safe_acl_name(self, acl: AccessControlList):
        return acl.label.replace(" ", "_")

    def parse_acl(self, acl: AccessControlList):
        label = self.safe_acl_name(acl)
        acl_type, * \
            _ = filter(lambda val: val["internalName"] == acl.type, ACL_TYPES)
        acl_type = acl_type.get("configName", "CONSISTENCY_ERROR")
        storage_path = Path(ENVIRONMENT.get("INSTANCE_PATH") +
                            ENVIRONMENT.get("SQUEEZY_FILE_STORAGE_PATH"))
        if acl.is_file:
            file: File = File.query.filter_by(id=acl.file_id).first()
            filepath = str(storage_path.absolute()) + "/" + \
                file.filepath
            line = f"# {file.label} ({file.original_filename})\nacl {label} {acl_type} -i \"{filepath}\"\n"
        else:
            line = f"acl {label} {acl_type} {acl.parameters}\n"
        
        logging.debug(f"parse_acl: got {line}")
        return line

    def parse_directive(self, directive: AccessDirective):
        def acl_negation(val): return "!" if val.negated else ""

        directive_type, * \
            _ = filter(lambda val: val["internalName"]
                       == directive.type, DIRECTIVE_TYPES)
        directive_type = directive_type.get("configName", "CONSISTENCY_ERROR")
        direction = "deny" if directive.deny else "allow"
        acls = " ".join(
            [f"{acl_negation(acl)}{self.safe_acl_name(acl.acl)}" for acl in directive.acls])
        line = f"{directive_type} {direction} {acls}\n"
        logging.debug(f"parse_directive: got {line}")
        return line

    def apply_config(self):
        logging.debug("apply_config: Will now build the config file")
        template_path = Path(ENVIRONMENT.get(
            "INSTANCE_PATH") + ENVIRONMENT.get("SQUID_TEMPLATE_DIR") + "/squid.conf.default")
        with open(template_path, "rt") as f:
            template = f.read()

        squid_config_keys = [(key, value) for key, value in ENVIRONMENT.items() if key.startswith("SQUEEZY_SQUID_CONFIG")]
        logging.debug(f"apply_config: Found {len(squid_config_keys)} configuration keys for the config file")
        for key, value in squid_config_keys:
            logging.debug(f"apply_config: Applying {key}: {value} to the config file")
            template = template.replace(f"${key}", value, 1)


        acls: list[AccessControlList] = AccessControlList.query.order_by(
            AccessControlList.priority).all()
        directives: list[AccessDirective] = AccessDirective.query.order_by(
            AccessDirective.priority).all()

        config_path = Path(ENVIRONMENT.get("INSTANCE_PATH") +
                           ENVIRONMENT.get("SQUID_CONFIG_DIR") + "/squid.conf")
        logging.debug(f"apply_config: Saving config file to {config_path}")
        with open(config_path, "w+t") as f:
            f.writelines([self.parse_acl(acl) for acl in acls])
            f.writelines([self.parse_directive(directive)
                         for directive in directives])
            f.write(template)

    def get_config(self):
        config_path = Path(ENVIRONMENT.get("INSTANCE_PATH") +
                           ENVIRONMENT.get("SQUID_CONFIG_DIR") + "/squid.conf")
        with open(config_path, "rt") as f:
            content = f.read()
        return content


    def reload_service(self):
        config_path = Path(ENVIRONMENT.get("INSTANCE_PATH") +
                           ENVIRONMENT.get("SQUID_CONFIG_DIR") + "/squid.conf")
        executable_path = ENVIRONMENT.get("SQUEEZY_SQUID_BINARY")
        proc: CompletedProcess = run(args=[executable_path, "-f", config_path.absolute(), "-k", "reconfigure"], capture_output=True)
        if proc.returncode == 0:
            return True
        else:
            utf8_stdout = str(proc.stdout, encoding="utf-8")
            utf8_stderr = str(proc.stderr, encoding="utf-8")
            logging.critical(f"reload_service: Squid failed to restart! Code: {proc.returncode}\nSTDOUT:\n{utf8_stdout}\nSTDERR:{utf8_stderr}")
            raise SqueezySquidReconfigureError(f"Squid failed to restart! Code: {proc.returncode}\nSTDOUT:\n{utf8_stdout}\nSTDERR:{utf8_stderr}")

    def get_file_content(self, path):
        p = Path(path)
        logging.debug(f"get_file_content: Trying to read {p.absolute()}")
        if not p.exists():
            logging.warning(f"get_file_content: Unable to open {p.absolute()}, returning empty content")
            return ""
        
        with open(p.absolute(), "rt") as f:
            file_content = f.read()

        return file_content

    def get_logs(self):
        logs = {
            "application": self.get_application_log(),
            "operational": self.get_operational_log(),
            "nginx": self.get_nginx_log(),
            "squid": self.get_squid_log(),
            "squid_access": self.get_squid_access_log(),
            "supervisor": self.get_supervisord_log(),
        }
        return logs


    def get_nginx_log(self):
        return self.get_file_content("/var/log/nginx/access.squeezy.log")

    def get_squid_log(self):
        return self.get_file_content("/var/log/squid/cache.log")

    def get_squid_access_log(self):
        return self.get_file_content("/var/log/squid/access.log")

    def get_supervisord_log(self):
        path = Path(ENVIRONMENT.get("INSTANCE_PATH") + "/logs/supervisord.log")
        return self.get_file_content(path)

    def get_operational_log(self):
        return self.get_file_content("/tmp/uwsgi.log")

    def get_application_log(self):
        path = Path(ENVIRONMENT.get("INSTANCE_PATH") + "/logs/application.log")
        return self.get_file_content(path.absolute())