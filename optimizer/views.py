import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import Driver, Job, Route, RouteStop
from .forms import DriverForm, JobForm, RouteOptimizeForm
from .geocoder import geocode
from .route_engine import optimize_route


# ─── Dashboard ────────────────────────────────────────────────────────────────

def dashboard(request):
    today = timezone.now().date()
    stats = {
        'total_jobs': Job.objects.count(),
        'pending_jobs': Job.objects.filter(status='pending').count(),
        'in_progress_jobs': Job.objects.filter(status='in_progress').count(),
        'completed_jobs': Job.objects.filter(status='completed').count(),
        'active_drivers': Driver.objects.filter(is_available=True).count(),
        'total_drivers': Driver.objects.count(),
        'total_routes': Route.objects.count(),
        'high_priority': Job.objects.filter(priority='high', status='pending').count(),
    }
    recent_jobs = Job.objects.select_related('driver').order_by('-created_at')[:8]
    recent_routes = Route.objects.select_related('driver').order_by('-created_at')[:5]
    drivers = Driver.objects.all()
    return render(request, 'optimizer/dashboard.html', {
        'stats': stats,
        'recent_jobs': recent_jobs,
        'recent_routes': recent_routes,
        'drivers': drivers,
    })


# ─── Jobs ─────────────────────────────────────────────────────────────────────

def job_list(request):
    qs = Job.objects.select_related('driver').all()

    priority = request.GET.get('priority')
    status = request.GET.get('status')
    driver_id = request.GET.get('driver')

    if priority:
        qs = qs.filter(priority=priority)
    if status:
        qs = qs.filter(status=status)
    if driver_id:
        qs = qs.filter(driver_id=driver_id)

    drivers = Driver.objects.all()
    return render(request, 'optimizer/job_list.html', {
        'jobs': qs,
        'drivers': drivers,
        'filter_priority': priority,
        'filter_status': status,
        'filter_driver': driver_id,
    })


def job_create(request):
    form = JobForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        job = form.save(commit=False)
        # If no coordinates provided, try geocoding the address
        if not job.latitude or not job.longitude:
            lat, lng = geocode(job.address)
            job.latitude = lat
            job.longitude = lng
            if not lat:
                messages.warning(request, "Couldn't auto-locate that address — you can add GPS coords manually later.")
        job.save()
        messages.success(request, f"Job for {job.customer_name} added.")
        return redirect('job_list')
    return render(request, 'optimizer/job_form.html', {'form': form, 'title': 'New Job'})


def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk)
    old_address = job.address
    form = JobForm(request.POST or None, instance=job)
    if request.method == 'POST' and form.is_valid():
        job = form.save(commit=False)
        # Re-geocode only if address changed and coords not manually supplied
        if job.address != old_address and not form.cleaned_data.get('latitude'):
            lat, lng = geocode(job.address)
            job.latitude = lat
            job.longitude = lng
        job.save()
        messages.success(request, "Job updated.")
        return redirect('job_list')
    return render(request, 'optimizer/job_form.html', {'form': form, 'title': 'Edit Job', 'job': job})


@require_POST
def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk)
    name = job.customer_name
    job.delete()
    messages.success(request, f"Job for {name} deleted.")
    return redirect('job_list')


@require_POST
def job_status_update(request, pk):
    job = get_object_or_404(Job, pk=pk)
    new_status = request.POST.get('status')
    if new_status in dict(Job.STATUS_CHOICES):
        job.status = new_status
        job.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': job.status, 'display': job.get_status_display()})
    return redirect('job_list')


# ─── Drivers ──────────────────────────────────────────────────────────────────

def driver_list(request):
    drivers = Driver.objects.prefetch_related('jobs').all()
    return render(request, 'optimizer/driver_list.html', {'drivers': drivers})


def driver_create(request):
    form = DriverForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        driver = form.save()
        messages.success(request, f"Driver {driver.name} added.")
        return redirect('driver_list')
    return render(request, 'optimizer/driver_form.html', {'form': form, 'title': 'New Driver'})


def driver_edit(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    form = DriverForm(request.POST or None, instance=driver)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Driver updated.")
        return redirect('driver_list')
    return render(request, 'optimizer/driver_form.html', {'form': form, 'title': 'Edit Driver', 'driver': driver})


@require_POST
def driver_delete(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    name = driver.name
    driver.delete()
    messages.success(request, f"Driver {name} removed.")
    return redirect('driver_list')


# ─── Routes ───────────────────────────────────────────────────────────────────

def route_list(request):
    routes = Route.objects.select_related('driver').all()
    return render(request, 'optimizer/route_list.html', {'routes': routes})


def route_optimize(request):
    form = RouteOptimizeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        jobs = list(form.cleaned_data['job_ids'])
        driver = form.cleaned_data.get('driver')
        name = form.cleaned_data.get('route_name') or f"Route — {timezone.now().strftime('%b %d %H:%M')}"
        depot_lat = form.cleaned_data.get('depot_lat')
        depot_lng = form.cleaned_data.get('depot_lng')

        ordered, total_km, duration_mins, savings_pct = optimize_route(
            jobs, depot_lat=depot_lat, depot_lng=depot_lng
        )

        route = Route.objects.create(
            name=name,
            driver=driver,
            total_distance_km=total_km,
            estimated_duration_mins=duration_mins,
            fuel_savings_pct=savings_pct,
        )
        for i, job in enumerate(ordered, start=1):
            RouteStop.objects.create(route=route, job=job, stop_order=i)

        messages.success(request, f"Route optimized — {len(ordered)} stops, {total_km} km.")
        return redirect('route_detail', pk=route.pk)

    pending_jobs = Job.objects.filter(status='pending').select_related('driver')
    return render(request, 'optimizer/route_optimize.html', {
        'form': form,
        'pending_jobs': pending_jobs,
    })


def route_detail(request, pk):
    route = get_object_or_404(Route, pk=pk)
    stops = route.routestop_set.select_related('job__driver').all()

    # Build GeoJSON-style data for the map
    waypoints = []
    for stop in stops:
        j = stop.job
        if j.has_coords():
            waypoints.append({
                'lat': j.latitude,
                'lng': j.longitude,
                'label': f"#{stop.stop_order} — {j.customer_name}",
                'priority': j.priority,
                'status': j.status,
                'address': j.address,
            })

    return render(request, 'optimizer/route_detail.html', {
        'route': route,
        'stops': stops,
        'waypoints_json': json.dumps(waypoints),
    })


@require_POST
def route_delete(request, pk):
    route = get_object_or_404(Route, pk=pk)
    name = str(route)
    route.delete()
    messages.success(request, f"{name} deleted.")
    return redirect('route_list')


# ─── API (JSON) ───────────────────────────────────────────────────────────────

def api_jobs(request):
    jobs = Job.objects.filter(latitude__isnull=False, longitude__isnull=False)
    data = [
        {
            'id': j.id,
            'customer': j.customer_name,
            'address': j.address,
            'lat': j.latitude,
            'lng': j.longitude,
            'priority': j.priority,
            'status': j.status,
            'service': j.get_service_type_display(),
        }
        for j in jobs
    ]
    return JsonResponse({'jobs': data})
