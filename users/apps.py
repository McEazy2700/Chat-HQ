from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self) -> None:
        import users.signals

        from users.models.auth import ServiceAPIKey

        try:
            if not ServiceAPIKey.objects.filter(
                id="30566d6e-4c38-40c6-9d83-1d4619439b2e"
            ).exists():
                _ = ServiceAPIKey.objects.create(
                    id="30566d6e-4c38-40c6-9d83-1d4619439b2e",
                    service_name="chat_messaging_service",
                    service_base_url="http://chat-messaging-web:8090",
                    service_user_logout_endpoint="/users/auth/service_user_auth_invalidate/",
                    key="mevMsCuACis8BWz-V2c-A7CYEl12zygU0AwpVfnq",
                    issuer_key="7SA-ync1eukN2oobKLJB_BRMT9zfDekaciu8pDDk",
                )
        except:
            pass

        return super().ready()
