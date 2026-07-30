from django.apps import AppConfig


class MyrecipejournalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myrecipejournal'

    def redy(self):
        import myrecipejournal.signals