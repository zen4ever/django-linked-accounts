from django import template

from linked_accounts.models import LinkedAccount


register = template.Library()


@register.filter
def linked_account(user, service):
    try:
        return LinkedAccount.objects.get(service=service, user=user)
    except LinkedAccount.DoesNotExist:
        return None
