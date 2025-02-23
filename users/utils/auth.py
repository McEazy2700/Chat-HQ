import logging
import requests
from users.models.auth import ServiceAPIKey
from users.models.users import User

logger = logging.getLogger(__name__)


class AuthManager:
    @classmethod
    def service_user_auth_invalidate(cls, user: User, service_key: ServiceAPIKey):
        url = (
            f"{service_key.service_base_url}{service_key.service_user_logout_endpoint}"
        )
        headers = {"X-Base-Auth-Service-Issuer-Key": service_key.issuer_key}
        data = {"hq_user_id": str(user.id)}
        response = requests.post(url, data, headers=headers)
        if response.status_code != 200:
            logger.error(f"Invalidate auth token failed: {response.text}")
