from django.contrib.gis.db import models
import uuid
# Create your models here.

class CrisisIncident(models.Model):
  SEVERITY_CHOICES=[
    ('LOW','Low / Resource Request'),
    ('MED','Medium / Road Blocked'),
    ('CRIT','Critical / Emergency'),
  ]
  id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
  title=models.CharField(max_length=200)
  description=models.TextField(blank=True)
  severity=models.CharField(max_length=4,choices=SEVERITY_CHOICES,default='LOW')
  location=models.PointField(srid=4326,null=True,blank=True)


  reported_at=models.DateTimeField(auto_now_add=True)
  is_resolved = models.BooleanField(default=False)
  
  def __str__(self):
    return f"[{self.severity} {self.title}]"
  

class Logisticshub(models.Model):
  name=models.CharField(max_length=200)
  location=models.PointField(srid=4326,null=True,blank=True)
  supplies_available=models.TextField(help_text="Comma separated list of items (e.g., Water, Meds)")
  def __str__(self):
    return self.name
class HazardZone(models.Model):
  name=models.CharField(max_length=200)
  boundary=models.MultiPolygonField(srid=4326)
  created_at=models.DateField(auto_now_add=True)
  def __str__(self):
    return f" Hazard Zone: {self.name}"