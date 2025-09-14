from celery import shared_task
from django.utils.timezone import now, timedelta
from .models import Survey
from .sockets import sio


@shared_task
def refresh_surveys():
    ten_minutes_ago = now() - timedelta(minutes=10)
    active_surveys = Survey.objects.filter(is_active=True)

    for survey in active_surveys:
        probability = survey.light_probability()

        # If probability < 45 → close survey
        if probability < 45:
            survey.is_active = False
            survey.save()
        else:
            # Prompt participants again
            for response in survey.responses.all():
                sio.emit("survey_prompt", {
                    "survey_id": survey.id,
                    "street": survey.street,
                    "city": survey.city,
                })

        # Broadcast update
        sio.emit("survey_update", {
            "street": survey.street,
            "city": survey.city,
            "probability": round(probability, 2),
            "status": "Likely Light" if probability >= 45 else "Likely No Light",
        })
