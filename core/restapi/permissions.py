from rest_framework.permissions import BasePermission

from apps.core.choices import PartnerType


class IsAuthenticated:
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request):
        return bool(request.user and request.user.is_authenticated)


class IsManagementUser(BasePermission):
    """
    Allows access only to management user.
    """

    def has_permission(self, request):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role.name.lower() == "superuser"
        )


class IsStoreUser(BasePermission):
    """
    Allows access only to store user.
    """

    def has_permission(self, request):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role.name.lower() == "store"
        )


class IsSubStoreUser(BasePermission):
    """
    Allows access only to store user.
    """

    def has_permission(self, request):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role.name.lower() == "substore"
        )


class IsLenderUser(BasePermission):
    """
    Allows access only to lender user with specific access_token and fingerprint agent.
    """

    def has_permission(self, request):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.storeId.partnerType == PartnerType.LENDER_MARKETPLACE
        )


class IsCustomerUser(BasePermission):

    def has_permission(self, request):
        """
        Allows access only to SubStore user with specific access_token and fingerprint agent.
        """
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role.name.lower() == "customer"
        )
