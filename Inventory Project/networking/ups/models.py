from django.db import models

class SNMP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    model = models.CharField(max_length=255)
    ups_type = models.CharField(max_length=255)
    battery_capacity = models.IntegerField()
    battery_temperature = models.IntegerField()
    battery_runtime_remain = models.BigIntegerField()
    battery_replace = models.BooleanField()
    battery_type = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    room_temperature = models.IntegerField()


class History(models.Model):
    snmp = models.ForeignKey(SNMP, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    model = models.CharField(max_length=255)
    ups_type = models.CharField(max_length=255)
    battery_capacity = models.IntegerField()
    battery_temperature = models.IntegerField()
    battery_runtime_remain = models.BigIntegerField()
    battery_replace = models.BooleanField()
    battery_type = models.CharField(max_length=255)

class Manual(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    building_name = models.CharField(max_length=255)
    lan_room = models.CharField(max_length=255)
    battery_installed_date = models.DateField()
    ups_installed_date = models.DateField()
    battery_count = models.IntegerField()
    management = models.CharField(max_length=255)
    last_modified_user = models.CharField(max_length=255)
    last_modified_date = models.DateTimeField(auto_now_add=False)
    battery_type = models.CharField(max_length=255)  # You can adjust the max_length as needed
    snmp = models.OneToOneField(SNMP, on_delete=models.CASCADE, null=True, blank=True)