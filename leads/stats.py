"""agent stats"""
import datetime
from .models import Agent


def calculate_stats(start_date, end_date, agent):
    """calculate leads stats for each agent in the specified time frame."""
    calls_made = agent.leads.filter(
        last_called__date__gte=start_date, last_called__date__lte=end_date
    )
    # calls_made = agent.leads.filter(last_called__date=start_date)
    calls_count = calls_made.count()
    answered_calls = calls_made.filter(tags__name="Answered")
    answered_calls_count = answered_calls.count()
    converted_leads = answered_calls.filter(category__name="Converted").count()
    # interested_leads = answered_calls.filter(category__name="Interested").count()
    # interested_leads = answered_calls.filter(
    #     tags__name__in=["Interested", "Answered"]
    # ).count()
    interested_leads = answered_calls.filter(tags__name="Interested").count()
    not_interested_leads = answered_calls.filter(
        category__name="Not Interested"
    ).count()
    try:
        conversion_rate = (converted_leads / answered_calls_count) * 100
    except ZeroDivisionError:
        conversion_rate = 0.0
    try:
        interested_rate = (interested_leads / answered_calls_count) * 100
    except ZeroDivisionError:
        interested_rate = 0.0
    try:
        not_interested_rate = (not_interested_leads / answered_calls_count) * 100
    except ZeroDivisionError:
        not_interested_rate = 0.0
    try:
        lost_rate = (interested_leads - converted_leads) / interested_leads * 100
    except ZeroDivisionError:
        lost_rate = 0.0

    return {
        "agent": f"{agent.user.first_name} {agent.user.last_name}",
        "calls made": calls_count,
        "answered calls": answered_calls_count,
        "conversion rate": f"{int(conversion_rate)}%",
        "interested rate": f"{int(interested_rate)}%",
        "lost rate": f"{int(lost_rate)}%",
        "not interested rate": f"{int(not_interested_rate)}%",
    }
