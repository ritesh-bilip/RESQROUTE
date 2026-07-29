from celery import shared_task
from .models import *
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@shared_task
def evaluate_incident_hazard_proximity(incident_id):
  try:
    incident=CrisisIncident.objects.get(id=incident_id)
    hazardous_zones = HazardZone.objects.filter(boundary__contains=incident.location)
    if hazardous_zones.exists():
      incident.severity='CRIT'
      incident.save()
      channel_layer=get_channel_layer()
      async_to_sync(channel_layer.group_send)(
        "map_updates",
        {
          "type":"incident_update",
          "data":{
            "action":"incident_updated",
            "incident_id":str(incident.id),
            "severity":incident.severity,
            "title":incident.title,
            "latitude":incident.location.y,
            "longitude":incident.location.x,
          }
        }
      )
      return f"Incident {incident_id} upgraded to CRITICAL"
  except CrisisIncident.DoesNotExist:
    return f"Incident {incident_id} not found"