from django.apps import AppConfig
import vinaigrette


class AccademicConfig(AppConfig):
    name = 'exoset.accademic'
    def ready(self):
        from .models import Sector
        vinaigrette.register(Sector, ['name', 'description'])
