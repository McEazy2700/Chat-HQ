import logging
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.db.models.base import ModelBase
from typing import Set, Optional
from users.models.users import User

from users.models.auth import ServiceAPIKey
from users.utils.auth import AuthManager

logger = logging.getLogger(__name__)


@receiver(m2m_changed, sender=User.user_permissions.through)
def user_permissions_changed(
    sender: ModelBase, instance: User, action: str, pk_set: Optional[Set[int]], **kwargs
) -> None:
    msg = f"{instance.email} permissions changed. Invalidating auth"
    print(msg)
    logger.info(msg)
    if action in ["post_add", "post_remove", "post_clear"]:
        service_keys = ServiceAPIKey.objects.all()
        for key in service_keys:
            msg = "Sending Invalidation request"
            logger.info(msg)
            print(msg)
            AuthManager.service_user_auth_invalidate(instance, key)


@receiver(m2m_changed, sender=User.groups.through)
def user_groups_changed(
    sender: ModelBase, instance: User, action: str, pk_set: Optional[Set[int]], **kwargs
) -> None:
    msg = f"{instance.email} groups changed. Invalidating auth"
    print(msg)
    logger.info(msg)
    if action in ["post_add", "post_remove", "post_clear"]:
        service_keys = ServiceAPIKey.objects.all()
        for key in service_keys:
            msg = "Sending Invalidation request"
            logger.info(msg)
            print(msg)
            AuthManager.service_user_auth_invalidate(instance, key)
