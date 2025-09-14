# main/socketio_docs.py
from drf_yasg import openapi

socketio_events = [
    {
        "event": "trigger_survey",
        "description": "Triggered by a user when they want to check if there's light in their area.",
        "payload": {
            "user_id": "string (external user ID)",
            "latitude": "float",
            "longitude": "float",
        },
        "response": {
            "survey_id": "integer",
            "street": "string",
            "city": "string",
        },
    },
    {
        "event": "survey_prompt",
        "description": "Emitted by the server to all nearby users when a survey is triggered.",
        "payload": {
            "survey_id": "integer",
            "street": "string",
            "city": "string",
        },
    },
    {
        "event": "survey_response",
        "description": "Sent by a user after answering the survey prompt.",
        "payload": {
            "survey_id": "integer",
            "user_id": "string",
            "response": "boolean (true=Yes, false=No)",
        },
    },
    {
        "event": "survey_update",
        "description": "Broadcast from server when survey responses update.",
        "payload": {
            "street": "string",
            "city": "string",
            "probability": "float",
            "status": "string (Likely Light / Likely No Light)",
        },
    },
]
