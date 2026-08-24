from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .services import build_dashboard


def dashboard(request):
    city = request.GET.get("city", "Deoghar").strip() or "Deoghar"
    try:
        data = build_dashboard(city)
        error = None
    except Exception as exc:
        data = None
        error = str(exc)
    return render(request, "weather/dashboard.html", {"data": data, "error": error, "searched_city": city})


@require_GET
def weather_api(request):
    city = request.GET.get("city", "Deoghar").strip() or "Deoghar"
    try:
        return JsonResponse(build_dashboard(city))
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)
