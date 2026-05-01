import uuid
from django.db import models

INDUSTRY_CHOICES = [
    ('tech', 'Technology'),
    ('health', 'Health & Wellness'),
    ('education', 'Education'),
    ('finance', 'Finance & Fintech'),
    ('retail', 'Retail & E-commerce'),
    ('food', 'Food & Beverage'),
    ('travel', 'Travel & Hospitality'),
    ('other', 'Other'),
]

VERDICT_CHOICES = [
    ('GO', 'Go'),
    ('CAUTION', 'Caution'),
    ('NO-GO', 'No-Go'),
]


class IdeaSubmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_key = models.CharField(max_length=40, db_index=True)
    title = models.CharField(max_length=80, blank=True)
    description = models.TextField()
    audience = models.CharField(max_length=200, blank=True)
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title or str(self.id)[:8]


class AnalysisReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.OneToOneField(IdeaSubmission, on_delete=models.CASCADE, related_name='report')
    verdict = models.CharField(max_length=10, choices=VERDICT_CHOICES)
    summary = models.TextField()
    market_score = models.IntegerField()
    feasibility_score = models.IntegerField()
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    opportunities = models.JSONField(default=list)
    threats = models.JSONField(default=list)
    risks = models.JSONField(default=list)
    next_steps = models.JSONField(default=list)
    model_used = models.CharField(max_length=100, blank=True)
    generation_ms = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.submission} — {self.verdict}"
