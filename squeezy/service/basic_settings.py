from database import db
from squeezy.models.settings import Settings
from squeezy.forms.settings import SettingsForm

class BasicSettingsService:

    def updateSettings(self, form: SettingsForm):
        settings = dict([(setting.key, setting) for setting in Settings.query.all()])
        for key, val in form.data.items():
            if settings.get(key, False):
                settings[key].value = val
        
        db.session.commit()

