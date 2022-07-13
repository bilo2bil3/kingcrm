from leads.models import Agent, Lead


def partition_leads(leads, agents_count):
    """split leads evenly between agents"""
    # to do so
    # we need to slice leads into N equal groups
    # where N is number of agents
    k, m = divmod(len(leads), agents_count)
    return [
        leads[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)]
        for i in range(agents_count)
    ]


def populate_db(leads_to_add, organisation, agent=None):
    """add leads to db."""
    for lead in leads_to_add:
        [
            first_name,
            last_name,
            source,
            service,
            email,
            country_code,
            phone_number,
            country,
            campaign,
            Q1,
            Q2,
            Q3,
            Q4,
        ] = lead

        phone_number = country_code + phone_number

        # skip lead if already exists in db
        if phone_number in Lead.objects.values_list("phone_number", flat=True):
            continue

        fields = {
            "organisation": organisation,
            "first_name": first_name,
            "last_name": last_name,
            "source": source,
            "service": service,
            "email": email,
            "phone_number": phone_number,
            "country": country,
            "campaign": campaign,
            "Q1": Q1,
            "Q2": Q2,
            "Q3": Q3,
            "Q4": Q4,
        }
        if agent is not None:
            fields["agent"] = agent

        Lead.objects.create(**fields)


def add_leads(agent=None, assign_randomly=False, leads_to_add=[], organisation=None):
    if agent is None and assign_randomly:
        agents, agents_count = Agent.objects.all(), Agent.objects.count()
        parts = partition_leads(leads_to_add, agents_count)
        for i, agent in enumerate(agents):
            leads_per_agent = parts[i]
            populate_db(leads_per_agent, organisation, agent)
        return
    populate_db(leads_to_add, organisation, agent)
