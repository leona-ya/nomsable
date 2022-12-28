from django import template

register = template.Library()

@register.filter
def serve_duration(iso_duration):
    total_seconds = int(iso_duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return ('' if hours == 0 else '{}h '.format(hours)) + ('' if minutes == 0 else '{}m'.format(minutes))