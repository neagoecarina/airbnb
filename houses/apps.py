from django.apps import AppConfig

class HousesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'houses'

    def ready(self):  # ← CORECT: în interiorul clasei
        import houses.signals
        print("✅ Signals loaded!")
