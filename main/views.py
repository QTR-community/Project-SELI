from django.shortcuts import render
from django.http import HttpResponse
from .models import Profile
from geopy.geocoders import Nominatim 
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Survey
# Create your views here.
from django.shortcuts import get_object_or_404
geolocator = Nominatim(user_agent="my_django_app")
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProfileSerializer

class CreateProfile(APIView):
    def post(self, request):
        # Step 1: validate basic input
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data["user_id"]
            street = serializer.validated_data["street"]
            city = serializer.validated_data["city"]
            state = serializer.validated_data["state"]

            # Step 2: geocode
            full_address = f"{street}, {city}, {state}, Nigeria"
            location = geolocator.geocode(full_address)
            if not location:
                return Response({"error": "Geocoding failed. Address not found."}, status=status.HTTP_400_BAD_REQUEST)

            # Step 3: save
            profile, created = Profile.objects.get_or_create(
                user_id=user_id,
                street=street,
                city=city,
                state=state,
                latitude=location.latitude,
                longitude=location.longitude
            )

            return Response(ProfileSerializer(profile).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateProfile(APIView):
    def patch(self, request, pk):
        profile = get_object_or_404(Profile, user_id=request.data.get("user_id"))

        # allow partial update
        serializer = ProfileSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            street = serializer.validated_data.get("street", profile.street)
            city = serializer.validated_data.get("city", profile.city)
            state = serializer.validated_data.get("state", profile.state)

            # rebuild address
            full_address = f"{street}, {city}, {state}, Nigeria"
            location = geolocator.geocode(full_address)

            if not location:
                return Response(
                    {"error": "Geocoding failed. Address not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # update profile
            profile.street = street
            profile.city = city
            profile.state = state
            profile.latitude = location.latitude
            profile.longitude = location.longitude
            profile.save()

            return Response(ProfileSerializer(profile).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def get_area_status(request, city, street):
    """
    Returns the latest survey status for a given street+city.
    Example: /api/surveys/Lagos/Opebi/
    """
    try:
        survey = Survey.objects.filter(city__iexact=city, street__iexact=street, is_active=True).latest("created_at")
    except Survey.DoesNotExist:
        return JsonResponse({
            "message": "No active survey for this area"
        }, status=404)

    probability = survey.light_probability()
    status = "Likely Light" if probability >= 45 else "Likely No Light"

    return JsonResponse({
        "street": survey.street,
        "city": survey.city,
        "probability": round(probability, 2),
        "status": status,
        "created_at": survey.created_at,
        "last_checked": survey.last_checked,
    })