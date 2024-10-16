from django.db import models

class Device(models.Model):
    ip_address = models.CharField(max_length=255)
    hostname = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    ssh_port = models.IntegerField(default=22)

    VENDOR_CHOICES = (
        ('mikrotik', 'Mikrotik'),
        ('cisco', 'Cisco')
    )
    vendor = models.CharField(max_length=255, choices=VENDOR_CHOICES)

    def __str__(self):
        return "{}. {}".format(self.id, self.ip_address)

class Log(models.Model):
    target = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    time = models.CharField(blank=True, max_length=255, null=True)
    messages = models.CharField(max_length=255)
    def __str__(self):
        return "{} - {} - {}".format(self.target, self.action, self.status)

class NetworkConnection(models.Model):
    local_address = models.CharField(max_length=50)
    remote_address = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    pid = models.IntegerField()

    def __str__(self):
        return f"{self.local_address} -> {self.remote_address} ({self.status})"

