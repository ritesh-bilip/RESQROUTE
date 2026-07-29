from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.contrib.gis.geos import Point
from .tasks import *
# Create your views here.

def control_center_map(request):
  return render(request,'core/map.html')
def map_data_api(request):
  incidents=[]
  for inc in CrisisIncident.objects.filter(is_resolved=False):
     incidents.append({
        'id':str(inc.id),
        'title':inc.title,
        'description':inc.description,
        'severity':inc.severity,
        'longitude':inc.location.x,
        'latitude':inc.location.y,
     })
  hubs=[]
  for hub in Logisticshub.objects.all():
        hubs.append({
            'id': str(hub.id),
            'name': hub.name,
            'longitude': hub.location.x,
            'latitude': hub.location.y,
            'supplies_available': hub.supplies_available
        })


  hazard_zones =[]
  for zone in HazardZone.objects.all():
     hazard_zones.append({
        'id':str(zone.id),
        'name':zone.name,
        'geojson':json.loads(zone.boundary.geojson)
     })
  
  
  
  return JsonResponse({'incidents': incidents, 'hubs': hubs,'hazard_zones':hazard_zones})

@csrf_exempt
def report_incident_api(request):
  """Endpoint for field workers to submit emergency pins."""
  if request.method == 'POST':
    try:
       data=json.loads(request.body)
       lat=float(data.get('latitude'))
       lng=float(data.get('longitude'))
       # Create a GeoDjango Point object: Point(longitude, latitude)
       Point=Point(lng,lat,srid=4326)
       incident=CrisisIncident.objects.create(
          title=data.get('title'),
          description=data.get('description',''),
          severity=data.get('severity','LOW'),
          location=Point
       )
       return JsonResponse ({'status':'success','incident_id':str(incident.id)},status=201)
    except Exception as e:
       return JsonResponse({'status':'error','message':str(e)},status=400)
  return JsonResponse({'status':'error','message':'Only post request allowed'},status=405)

@csrf_exempt
def report_incident_api(request):
   if request.method=='POST':
      try:
         data=json.loads(request.body)
         lat=float(data.get('latitude'))
         lng=float(data.get('longitude'))

         point=Point(lng,lat,srid=4326)

         incident=CrisisIncident.objects.create(
            title=data.get('title'),
            description=data.get('description', ''),
            severity=data.get('severity','LOW'),
            location=point,
                              )
         evaluate_incident_hazard_proximity.delay(str(incident.id))
         return JsonResponse({'status':'succes','incident_id': str(incident.id)},status=201)
      except Exception as e:
         return JsonResponse({'status':'error','message':str(e)},status=400)
   return JsonResponse({'status':'error','message':'Only POST allowed'},status=405)