from django.db import models


class Profile(models.Model):
    # Store external user_id coming from Node.js auth system
    user_id = models.CharField(max_length=100, unique=True)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    #postal_code = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"User {self.user_id} - {self.city}, {self.state}"
    

class Survey(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_checked = models.DateTimeField(auto_now=True)

    def light_probability(self):
        total = self.responses.count()
        if total == 0:
            return 0
        return (self.responses.filter(response=True).count() / total) * 100


class SurveyResponse(models.Model):
    survey = models.ForeignKey(Survey, related_name="responses", on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    response = models.BooleanField(default=True)  # YES if confirmed
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("survey", "profile")
