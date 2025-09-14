import socketio
import logging
from geopy.geocoders import Nominatim
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist
from .models import Profile, Survey, SurveyResponse

logger = logging.getLogger(__name__)

# Socket.IO + Geopy Setup
sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)
geolocator = Nominatim(user_agent="survey_app")


def _get_room_name(street, city):
    """Generate a unique Socket.IO room name based on location."""
    return f"{street}_{city}".replace(" ", "_").lower()


@sio.event
def connect(sid, environ):
    logger.info(f"🔗 Client connected: {sid}")


@sio.event
def disconnect(sid):
    logger.info(f"❌ Client disconnected: {sid}")


@sio.event
def trigger_survey(sid, data):
    """
    Triggered from frontend when a user sends latitude/longitude.
    Creates a survey and notifies users in the same area.
    """
    try:
        latitude = data["latitude"]
        longitude = data["longitude"]
        user_id = data["user_id"]

        logger.info(f"📡 trigger_survey received from {user_id}: {latitude}, {longitude}")

        location = geolocator.reverse(f"{latitude}, {longitude}")
        if not location:
            logger.warning("⚠️ No location found for given coordinates.")
            return

        street = location.raw["address"].get("road")
        city = location.raw["address"].get("city")
        state = location.raw["address"].get("state")

        if not street or not city:
            logger.warning("⚠️ Missing street or city in geocoding result.")
            return

        # Create survey in DB
        survey = Survey.objects.create(street=street, city=city, state=state)

        # Generate a room for this street+city and add current user
        room = _get_room_name(street, city)
        sio.enter_room(sid, room)
        logger.info(f"🏠 {user_id} joined room: {room}")

        # Find other profiles in same street + city
        profiles = Profile.objects.filter(street=street, city=city)

        for p in profiles.exclude(user_id=user_id):
            # (Optional: you might want to map profile -> sid to join them to the room)
            pass

        # Emit to everyone in the same room
        sio.emit(
            "survey_prompt",
            {
                "survey_id": survey.id,
                "street": street,
                "city": city,
            },
            room=room
        )

    except Exception as e:
        logger.exception(f"❌ Error in trigger_survey: {e}")


@sio.event
def survey_response(sid, data):
    """
    Called when a user submits a survey response.
    Updates the Survey and broadcasts to the same room (street+city).
    """
    try:
        survey_id = data.get("survey_id")
        user_id = data.get("user_id")
        response = data.get("response")

        if not all([survey_id, user_id, response]):
            logger.warning(f"⚠️ Missing data in survey_response: {data}")
            return

        survey = Survey.objects.get(id=survey_id)
        profile = Profile.objects.get(user_id=user_id)

        # Add this user to the survey's room (if not already in it)
        room = _get_room_name(survey.street, survey.city)
        sio.enter_room(sid, room)
        logger.info(f"🏠 {user_id} joined room: {room}")

        # Create or update the survey response
        SurveyResponse.objects.update_or_create(
            survey=survey,
            profile=profile,
            defaults={"response": response, "updated_at": now()}
        )

        probability = survey.light_probability()
        status = "Likely Light" if probability >= 45 else "Likely No Light"

        logger.info(f"📊 Survey updated: {survey.street} {survey.city} → {probability}%")

        # Emit update only to users in the same room
        sio.emit(
            "survey_update",
            {
                "street": survey.street,
                "city": survey.city,
                "probability": round(probability, 2),
                "status": status,
            },
            room=room
        )

        # If probability is too low, deactivate the survey
        if probability < 45:
            survey.is_active = False
            survey.save()
            logger.info(f"⛔ Survey {survey.id} marked inactive (low probability).")

    except ObjectDoesNotExist:
        logger.error(f"❌ Survey or Profile not found for data: {data}")
    except Exception as e:
        logger.exception(f"❌ Error in survey_response: {e}")
