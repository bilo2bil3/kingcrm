from django import template
from leads.models import Agent

register = template.Library()

@register.filter
def in_permissions(agent_permissions, permission):
    return agent_permissions.filter(code=permission.code)

@register.filter
def has_permissions(user, permission):
    print(user.id, permission)
    try:
        agent = Agent.objects.get(user=user)
        try:
            print("Second Tryyyy", permission)
            print(agent.permissions.all())
            agent.permissions.get(code=permission)
            return True
        except:
            pass
    except Agent.DoesNotExist:
        if user.is_superuser:
            return True
    return False