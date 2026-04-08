from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.forms import ModelForm
from django import forms
from .models import Client, Artist, Service, Appointment, NailDesign, Review, ReviewEditLog, NailArtImageLibrary, ActivityLog, ArtistAvailability

class ArtistAdminForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False, help_text="Leave blank to keep current password")
    
    class Meta:
        model = Artist
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # For existing artists, show current password as masked
            self.fields['password'].widget.attrs['placeholder'] = 'Enter new password (optional)'
    
    def save(self, commit=True):
        artist = super().save(commit=False)
        # Only hash and save password if it's provided and not already hashed
        if self.cleaned_data.get('password') and not self.cleaned_data['password'].startswith('pbkdf2_sha256$'):
            artist.set_password(self.cleaned_data['password'])
        elif commit and not artist.password:
            # Ensure password is never empty
            artist.set_password('default123')
        if commit:
            artist.save()
        return artist

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    form = ArtistAdminForm
    list_display = ('get_full_name', 'get_email', 'phone', 'status', 'is_active_employee', 'created_at')
    list_filter = ('status', 'is_active_employee', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Artist Information', {
            'fields': ('user', 'first_name', 'last_name', 'email', 'password', 'phone')
        }),
        ('Status', {
            'fields': ('status', 'is_active_employee', 'sanitation_until')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj and obj.pk and obj.user:  # Editing existing object with linked user
            readonly.append('user')  # Don't allow changing the linked user
        return readonly

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'service', 'artist', 'date', 'time', 'status', 'proposed_date', 'proposed_time', 'reschedule_lock_expires_at')
    list_filter = ('status', 'date', 'artist')
    search_fields = ('client__email', 'service__name')
    readonly_fields = ('reschedule_lock_expires_at',)

@admin.register(NailDesign)
class NailDesignAdmin(admin.ModelAdmin):
    list_display = ('title', 'tags', 'service', 'is_active', 'created_at')
    list_filter = ('is_active', 'service')
    search_fields = ('title', 'tags')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'appointment', 'artist', 'client', 'rating', 'is_verified', 'health_safety_flag', 'created_at')
    list_filter = ('is_verified', 'health_safety_flag', 'rating', 'created_at')
    search_fields = ('appointment__service__name', 'artist__user__email', 'client__email', 'comment')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ReviewEditLog)
class ReviewEditLogAdmin(admin.ModelAdmin):
    list_display = ('review', 'editor', 'old_rating', 'edited_at')
    list_filter = ('edited_at', 'old_health_safety_flag')
    search_fields = ('review__appointment__service__name', 'editor__email', 'old_comment')
    readonly_fields = ('review', 'editor', 'old_rating', 'old_comment', 'old_health_safety_flag', 'edited_at')


@admin.register(NailArtImageLibrary)
class NailArtImageLibraryAdmin(admin.ModelAdmin):
    list_display = ('title', 'style_key', 'weight_minutes', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'style_key')

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('get_user_identifier', 'get_activity_type_display', 'description', 'ip_address', 'timestamp')
    list_filter = ('user_type', 'activity_type', 'timestamp', 'appointment', 'service')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'artist__first_name', 'artist__last_name', 'artist__email', 'description', 'ip_address')
    readonly_fields = ('timestamp', 'get_user_identifier', 'get_metadata_display')
    
    fieldsets = (
        ('Activity Information', {
            'fields': ('user_type', 'user', 'artist', 'activity_type', 'description')
        }),
        ('Related Objects', {
            'fields': ('appointment', 'service'),
            'classes': ('collapse',)
        }),
        ('Technical Details', {
            'fields': ('ip_address', 'user_agent', 'timestamp', 'get_metadata_display'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_identifier(self, obj):
        return obj.get_user_identifier()
    get_user_identifier.short_description = 'User'
    
    def get_metadata_display(self, obj):
        if obj.metadata:
            import json
            return json.dumps(obj.metadata, indent=2, sort_keys=True)
        return 'None'
    get_metadata_display.short_description = 'Metadata'
    
    def has_add_permission(self, request):
        # Prevent manual creation of activity logs
        return False
    
    def has_change_permission(self, request, obj=None):
        # Allow viewing but prevent editing
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Allow deletion for cleanup purposes
        return request.user.is_superuser

admin.site.register(Client)
admin.site.register(Service)

@admin.register(ArtistAvailability)
class ArtistAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('artist', 'get_working_days', 'slot_duration', 'created_at', 'updated_at')
    list_filter = ('slot_duration', 'created_at')
    search_fields = ('artist__first_name', 'artist__last_name', 'artist__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Artist', {
            'fields': ('artist',)
        }),
        ('Weekday Hours', {
            'fields': (
                ('monday_start', 'monday_end'),
                ('tuesday_start', 'tuesday_end'),
                ('wednesday_start', 'wednesday_end'),
                ('thursday_start', 'thursday_end'),
                ('friday_start', 'friday_end'),
                ('saturday_start', 'saturday_end'),
                ('sunday_start', 'sunday_end'),
            )
        }),
        ('Settings', {
            'fields': ('slot_duration', 'break_start', 'break_end')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_working_days(self, obj):
        days = []
        day_fields = [
            ('monday', 'Mon'),
            ('tuesday', 'Tue'), 
            ('wednesday', 'Wed'),
            ('thursday', 'Thu'),
            ('friday', 'Fri'),
            ('saturday', 'Sat'),
            ('sunday', 'Sun')
        ]
        
        for day_field, day_name in day_fields:
            start_field = f'{day_field}_start'
            end_field = f'{day_field}_end'
            if getattr(obj, start_field) and getattr(obj, end_field):
                days.append(day_name)
        
        return ', '.join(days) if days else 'None'
    get_working_days.short_description = 'Working Days'