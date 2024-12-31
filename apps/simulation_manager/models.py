from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.files.storage import default_storage as storage
import uuid
import os


class Simulation(models.Model):

    # meta data
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name        = models.CharField(max_length=100, blank=False, null=False, default="Simulation")
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='simulations')

    # simulation data
    yaml_file = models.FileField(upload_to='yaml_files/')

    def __str__(self):
        return f"{self.id} {self.created_at} {self.updated_at} {self.created_by.username} {self.name} {self.yaml_file}"
    
def rename_yaml_file(instance, filename):
    ext = filename.split('.')[-1]  # get file extension
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('yaml_files', filename)

@receiver(pre_save, sender=Simulation)
def update_filename(sender, instance, **kwargs):
    if instance.pk:
        initial_path = instance.yaml_file.path
        new_name = f'{instance.id}_simulation.yaml'

        if storage.exists(initial_path):
            storage.delete(new_name)  # Delete the file if it already exists
            storage.save(new_name, storage.open(initial_path))
            storage.delete(initial_path)

        instance.yaml_file.name = new_name