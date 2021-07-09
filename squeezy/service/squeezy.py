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
import os


class SqueezyServiceFileFormatError(Exception):
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
        storage_path = ENVIRONMENT.get("SQUEEZY_FILE_STORAGE_PATH")
        filepath = os.path.join(ENVIRONMENT.get(
            "INSTANCE_PATH"), storage_path, f"file_{on_disk_name}")
        normalized_path = Path(filepath)
        file_db.filepath = str(normalized_path.absolute())
        with open(normalized_path.absolute(), "w+b") as f:
            data.save(f)
            f.seek(0)
            file_db.sha256 = sha256(f.read()).hexdigest()
        db.session.add(file_db)
        db.session.commit()

    def handle_file_read(self, file: File):
        with open(file.filepath, "rt", encoding="utf-8") as f:
            return f.read()

    def handle_file_delete(self, file: File):
        os.unlink(file.filepath)
        db.session.delete(file)
        db.session.commit()

    def update_acl(self, acl_data: dict):
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

        return acl.id


    def delete_acl(self, acl_data: dict):
        id = acl_data["id"]
        if id != -1:
            acl = AccessControlList.query.filter_by(id=id).first()
        else:
            raise Exception("No id provided")
        
        if not acl:
            raise Exception("ACL does not exist")

        db.session.delete(acl)
        db.session.commit()

        return id

    def delete_directive(self, directive_data: dict):
        id = directive_data["id"]
        if id != -1:
            directive: AccessDirective = AccessDirective.query.filter_by(id=id).first()
        else:
            raise Exception("No id provided")
        
        for acldir in directive.acls:
            db.session.delete(acldir)

        if not directive:
            raise Exception("Directive does not exist")

        db.session.delete(directive)
        db.session.commit()

        return id


    def update_directive(self, directive_data: dict):
        id = directive_data["id"]
        if id != -1:
            directive = AccessDirective.query.filter_by(id=id).first()
        else:
            directive = AccessDirective()

        if not directive:
            raise Exception("Wrong Directive id")
        
        oldAcls = list(directive.acls)

        existingAcls = [(ACLDirective.query.filter_by(id=acldata["acldir_id"]).first(), acldata) for acldata in directive_data["acls"] if acldata["acldir_id"] != -1]
        for acldir, acldata in existingAcls:
            acl = AccessControlList.query.filter_by(id=acldata["id"]).first()
            acldir.negated = acldata["negated"]
            acldir.acl = acl


        newAcls = [acldata for acldata in directive_data["acls"] if acldata["acldir_id"] == -1 and acldata["id"] != -1]
        for newAcl in newAcls:
            aclDirective = ACLDirective()
            acl = AccessControlList.query.filter_by(id=newAcl["id"]).first()
            if not acl:
                raise Exception("Non-existing ACL provided", newAcl)
            
            aclDirective.acl = acl
            aclDirective.directive = directive
            aclDirective.negated = newAcl["negated"]
            db.session.add(aclDirective)

        removedAcls = [aclToRemove for aclToRemove in oldAcls if aclToRemove not in existingAcls[0]]
        for removedAcl in removedAcls:
            db.session.delete(removedAcl)
        
        directive.type = directive_data["type"]
        directive.priority = directive_data["priority"]
        directive.deny = directive_data["deny"]

        db.session.add(directive)
        db.session.commit()

        return directive


    def apply_config(self):
        negation_c = "!"
        empty_c = ""
        template_path = Path(ENVIRONMENT.get("INSTANCE_PATH") + ENVIRONMENT.get("SQUID_TEMPLATE_DIR") + "/squid.conf.default")
        with open(template_path, "rt") as f:
            template = f.read()
        
        acls: list[AccessControlList] = AccessControlList.query.order_by(AccessControlList.priority).all()
        directives: list[AccessDirective] = AccessDirective.query.order_by(AccessDirective.priority).all()

        config_path = Path(ENVIRONMENT.get("INSTANCE_PATH") + ENVIRONMENT.get("SQUID_CONFIG_DIR") + "/squid.conf")
        with open(config_path, "w+t") as f:
            f.writelines(
                [
                    "acl %s %s %s\n" % 
                        (
                            acl.label.replace(" ", "_"), 
                            [acl_type["configName"] for acl_type in ACL_TYPES if acl_type["internalName"] == acl.type][0],
                            "-i \"" + File.query.filter_by(id=acl.file_id).first().filepath + "\"" if acl.is_file else acl.parameters 
                        ) 
                    for acl in acls
                ])
            f.writelines([
                "%s %s %s\n" %
                    (
                        [directive_type["configName"] for directive_type in DIRECTIVE_TYPES if directive_type["internalName"] == directive.type][0],
                        "deny" if directive.deny else "allow",
                        " ".join([f"{negation_c if acl.negated else empty_c}{acl.acl.label}" for acl in directive.acls])
                    )
                for directive in directives
                ])
            f.write(template)
            f.seek(0)
            config_content = f.read()
        
        return config_content

