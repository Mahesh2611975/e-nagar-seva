from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# -------------------------------
# 👤 Profile
# -------------------------------
ROLE_CHOICES = (
    ('citizen', 'Citizen'),
    ('officer', 'Officer'),
)

from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = [
        ('citizen', 'Citizen'),
        ('officer', 'Officer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    coins = models.IntegerField(default=0)
    def __str__(self):
        return self.user.username


# -------------------------------
# 📸 Complaint
# -------------------------------
CATEGORY_CHOICES = [
    ('road', 'Road Issue'),
    ('water', 'Water Problem'),
    ('electricity', 'Electricity'),
    ('garbage', 'Garbage'),
    ('other', 'Other'),
]

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('in_progress', 'In Progress'),
    ('resolved', 'Resolved'),
]

class Complaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    department = models.CharField(max_length=100, default="General")

    image = models.ImageField(upload_to='complaints/')
    description = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    assigned_officer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_complaints'
    )

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.category} - {self.status}"


# -------------------------------
# 👮 Officer
# -------------------------------
class Officer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)


# -------------------------------
# 🔄 Updates
# -------------------------------
class Update(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='updates/', blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    description = models.TextField()

    assigned_officer = models.ForeignKey(
        Officer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )


# -------------------------------
# 🔔 Notification
# -------------------------------
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    image = models.ImageField(upload_to='notifications/', null=True, blank=True)  # ✅ MUST