from django.urls import reverse
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser

from permissions.models import Permission


class User(AbstractUser):
    is_organisor = models.BooleanField(default=True)
    is_agent = models.BooleanField(default=False)
    click2call_extension = models.CharField(max_length=3)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class LeadManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()


class Lead(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    source = models.CharField(max_length=64, default="")
    service = models.CharField(max_length=64, default="")
    age = models.IntegerField(default=0)
    organisation = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    agent = models.ForeignKey(
        "Agent", null=True, blank=True, on_delete=models.SET_NULL, related_name="leads"
    )
    category = models.ForeignKey(
        "Category",
        related_name="leads",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    description = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    profile_picture = models.ImageField(
        null=True, blank=True, upload_to="profile_pictures/"
    )
    converted_date = models.DateTimeField(null=True, blank=True)
    country = models.CharField(max_length=64, default="")
    campaign = models.CharField(max_length=64, default="")
    tags = models.ManyToManyField("Tag", related_name="leads", blank=True)
    last_called = models.DateTimeField(blank=True, null=True)

    objects = LeadManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


def handle_upload_follow_ups(instance, filename):
    return f"lead_followups/lead_{instance.lead.pk}/{filename}"


class FollowUp(models.Model):
    lead = models.ForeignKey(Lead, related_name="followups", on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    file = models.FileField(null=True, blank=True, upload_to=handle_upload_follow_ups)

    def __str__(self):
        return f"{self.lead.first_name} {self.lead.last_name}"


class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organisation = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    permissions = models.ManyToManyField(Permission, related_name='agent_permissions', blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Category(models.Model):
    name = models.CharField(max_length=30)  # New, Contacted, Converted, Unconverted
    organisation = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


def post_user_created_signal(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


post_save.connect(post_user_created_signal, sender=User)

### load from google sheets ###
class LeadsSheet(models.Model):
    source = models.CharField(max_length=64)
    url = models.URLField()
    sheet_name = models.CharField(max_length=64)
    organisation = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    agent = models.ForeignKey("Agent", blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.url


class SalesReport(models.Model):
    EMPTY_CHOICE = [(None, "-" * 10)]

    # agent
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="reports")

    # month
    MONTHS = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    MONTH_CHOICES = EMPTY_CHOICE + [(str(i), m) for i, m in enumerate(MONTHS, start=1)]
    month = models.CharField(max_length=2, choices=MONTH_CHOICES)

    # year
    CURRENT_YEAR = 2022
    YEAR_CHOICES = EMPTY_CHOICE + [
        (str(i), str(i)) for i in range(CURRENT_YEAR - 10, CURRENT_YEAR + 1)
    ]
    year = models.CharField(max_length=4, choices=YEAR_CHOICES)

    # questions
    PERFORMANCE_CHOICES = EMPTY_CHOICE + [
        ("100", "Excellent"),
        ("75", "Good"),
        ("50", "Needs improvement"),
        ("25", "Bad"),
    ]
    performance = models.CharField(
        max_length=3,
        choices=PERFORMANCE_CHOICES,
        verbose_name="What you think about this agent sales performance this month?",
    )
    KPI_RATE_CHOICES = EMPTY_CHOICE + [
        ("100", "80% - 100%"),
        ("75", "60% - 80%"),
        ("50", "40% - 60%"),
        ("25", "0%"),
    ]
    kpi_rate = models.CharField(
        max_length=3,
        choices=KPI_RATE_CHOICES,
        verbose_name="What KPI rate he deserves this month?",
    )
    REVENU_CHOICES = EMPTY_CHOICE + [
        ("100", "10,000$ - $50,000"),
        ("75", "5000$ - $10,000"),
        ("50", "1000$ - $5000"),
        ("25", "0$ - $1000"),
    ]
    revenu = models.CharField(
        max_length=3,
        choices=REVENU_CHOICES,
        verbose_name="How much revenue the sales agent made this month?",
    )
    BEST_SERVICE_CHOICES = EMPTY_CHOICE + [
        ("100", "Copy Trading"),
        ("75", "Course"),
        ("50", "Signals"),
        ("25", "Consultation"),
    ]
    best_service = models.CharField(
        max_length=3,
        choices=BEST_SERVICE_CHOICES,
        verbose_name="Which service you think he's best at this month?",
    )
    CUSTOMER_SUPPORT_CHOICES = EMPTY_CHOICE + [
        ("100", "80% - 100%"),
        ("75", "60% - 80%"),
        ("50", "40% - 60%"),
        ("25", "0%"),
    ]
    customer_support = models.CharField(
        max_length=3,
        choices=CUSTOMER_SUPPORT_CHOICES,
        verbose_name="Customer Support Performance?",
    )
    total_rate = models.CharField(max_length=3)

    def __str__(self) -> str:
        return f"{self.agent} sales report {self.month}/{self.year}"

    def get_absolute_url(self):
        return reverse("leads:sales-report-list")
