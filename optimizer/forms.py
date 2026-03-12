from django import forms
from .models import Driver, Job, Route


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['name', 'phone', 'vehicle_type', 'max_daily_distance', 'is_available']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Full name'}),
            'phone': forms.TextInput(attrs={'placeholder': '(555) 000-0000'}),
            'max_daily_distance': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
        }


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'customer_name', 'address', 'latitude', 'longitude',
            'service_type', 'priority', 'time_window_start', 'time_window_end',
            'driver', 'status', 'notes',
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={'placeholder': 'Customer full name'}),
            'address': forms.TextInput(attrs={'placeholder': '123 Main St, City, State'}),
            'latitude': forms.NumberInput(attrs={'step': 'any', 'placeholder': 'Auto-filled'}),
            'longitude': forms.NumberInput(attrs={'step': 'any', 'placeholder': 'Auto-filled'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any special instructions...'}),
            'time_window_start': forms.TimeInput(attrs={'type': 'time'}),
            'time_window_end': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned = super().clean()
        t_start = cleaned.get('time_window_start')
        t_end = cleaned.get('time_window_end')
        if t_start and t_end and t_end <= t_start:
            raise forms.ValidationError("Time window end must be after start.")
        return cleaned


class RouteOptimizeForm(forms.Form):
    driver = forms.ModelChoiceField(
        queryset=Driver.objects.filter(is_available=True),
        required=False,
        empty_label="— Unassigned —",
        help_text="Optional: assign a driver to this route.",
    )
    route_name = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Morning Run — North Side'}),
        help_text="Give this route a memorable name.",
    )
    job_ids = forms.ModelMultipleChoiceField(
        queryset=Job.objects.filter(status='pending'),
        widget=forms.CheckboxSelectMultiple,
        help_text="Select the stops to include in this route.",
    )
    depot_lat = forms.FloatField(
        required=False, widget=forms.HiddenInput()
    )
    depot_lng = forms.FloatField(
        required=False, widget=forms.HiddenInput()
    )

    def clean_job_ids(self):
        jobs = self.cleaned_data.get('job_ids')
        if not jobs or len(jobs) < 2:
            raise forms.ValidationError("Select at least 2 jobs to optimize a route.")
        return jobs
