from django.apps import AppConfig


class GithubadminConfig(AppConfig):
    name = 'exoset.githubadmin'
    verbose_name = "Githubadmin"

    def ready(self):
        try:
            import exoset.githubadmin.signals  # noqa F401
        except ImportError:
            pass

