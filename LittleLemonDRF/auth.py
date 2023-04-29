from rest_framework.permissions import IsAuthenticated, IsAdminUser


def is_admin(request):
    return request.user.is_superuser or request.user.is_staff


def is_manager(request):
    return request.user.groups.filter(name="manager").exists()


def is_customer(request):
    return not request.user.groups.exists() and not is_admin(request)


def is_delivery_crew(request):
    print("DD :: ", request.user.groups.filter(name="delivery-crew"))
    return request.user.groups.filter(name="delivery-crew").exists()


class IsManager(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if not request.user.groups.filter(name='manager').exists():
            return False
        return True


class IsCustomer(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if request.user.groups.exists() is False and not is_admin(request):
            return True
        return False
