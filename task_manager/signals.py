from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Task


@receiver(pre_save, sender=Task)
def track_status_change(sender, instance, **kwargs):
    try:
        old_instance = sender.objects.get(pk=instance.pk)
        instance._previous_status = old_instance.status
    except sender.DoesNotExist:
        instance._previous_status = None


@receiver(post_save, sender=Task)
def send_status_change_notification(sender, instance, created, **kwargs):
    if not created and hasattr(instance, '_previous_status') and instance._previous_status != instance.status:
        is_closed = instance.status == 'done'
        subject = f'Task "{instance.title}" {"Closed" if is_closed else "Status Changed"}'
        message = render_to_string('task_manager/email/task_status_change.txt', {
            'task': instance,
            'new_status': instance.get_status_display(),
            'is_closed': is_closed,
        })
        recipient_email = instance.owner.email

        send_mail(
            subject=subject,
            message=message,
            from_email='noreply@ich.com',
            recipient_list=[recipient_email],
            fail_silently=False,
        )