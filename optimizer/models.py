from django.db import models


class Driver(models.Model):
    VEHICLE_CHOICES = [
        ('van', 'Van'),
        ('truck', 'Truck'),
        ('car', 'Car'),
        ('motorcycle', 'Motorcycle'),
        ('bike', 'Bike'),
    ]

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_CHOICES, default='van')
    max_daily_distance = models.FloatField(default=200.0)  # miles
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def pending_jobs_count(self):
        return self.jobs.filter(status='pending').count()

    def completed_jobs_count(self):
        return self.jobs.filter(status='completed').count()


class Job(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    SERVICE_CHOICES = [
        ('delivery', 'Delivery'),
        ('pickup', 'Pickup'),
        ('cleaning', 'Cleaning'),
        ('lawn_care', 'Lawn Care'),
        ('repair', 'Repair'),
        ('inspection', 'Inspection'),
        ('other', 'Other'),
    ]

    customer_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES, default='delivery')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    time_window_start = models.TimeField(null=True, blank=True)
    time_window_end = models.TimeField(null=True, blank=True)
    driver = models.ForeignKey(
        Driver, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='jobs'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer_name} — {self.address}"

    def has_coords(self):
        return self.latitude is not None and self.longitude is not None


class Route(models.Model):
    name = models.CharField(max_length=100, blank=True)
    driver = models.ForeignKey(
        Driver, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='routes'
    )
    jobs = models.ManyToManyField(Job, through='RouteStop', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_distance_mi = models.FloatField(default=0.0)
    estimated_duration_mins = models.IntegerField(default=0)
    fuel_savings_pct = models.FloatField(default=0.0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name or f"Route #{self.pk}"

    def stop_count(self):
        return self.routestop_set.count()

    def fuel_saved_gallons(self):
        if self.fuel_savings_pct <= 0 or self.total_distance_mi <= 0:
            return 0.0
        base_mi = self.total_distance_mi / max(1 - self.fuel_savings_pct / 100, 0.01)
        saved_mi = base_mi - self.total_distance_mi
        return round(saved_mi * 0.05, 2)  # ~0.05 gal/mi for a light van


class RouteStop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    stop_order = models.PositiveIntegerField()

    class Meta:
        ordering = ['stop_order']
        unique_together = ('route', 'stop_order')

    def __str__(self):
        return f"Stop {self.stop_order}: {self.job.customer_name}"
