from django import template

register = template.Library()

@register.filter
def status_color(status):
    """Return Bootstrap color class for appointment status"""
    status_colors = {
        'Waiting': 'warning',
        'Approved': 'success',
        'Rescheduling': 'info',
        'On-going': 'primary',
        'Finished': 'secondary',
        'Cancelled': 'danger',
    }
    return status_colors.get(status, 'secondary')

@register.filter
def status_display(status):
    """Return user-friendly display text for appointment status"""
    status_display_map = {
        'Waiting': 'Pending',
        'Approved': 'Confirmed',
        'Rescheduling': 'Rescheduling',
        'On-going': 'In Progress',
        'Finished': 'Completed',
        'Cancelled': 'Cancelled',
    }
    return status_display_map.get(status, status)
