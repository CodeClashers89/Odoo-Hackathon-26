import datetime
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from drivers.models import Driver

class Command(BaseCommand):
    help = 'Sends email notifications to drivers whose driving licenses are expiring within 30 days or have expired.'

    def handle(self, *args, **options):
        self.stdout.write("Checking for expiring driver licenses...")
        today = datetime.date.today()
        threshold_date = today + datetime.timedelta(days=30)
        
        # Get all drivers whose license is expired or expiring in the next 30 days
        expiring_drivers = Driver.objects.filter(license_expiry_date__lte=threshold_date)
        
        sent_count = 0
        skipped_count = 0
        failed_count = 0
        
        for driver in expiring_drivers:
            if not driver.user or not driver.user.email:
                self.stdout.write(self.style.WARNING(
                    f"Skipped driver '{driver.name}': No user account or email address associated."
                ))
                skipped_count += 1
                continue
                
            is_expired = driver.license_expiry_date < today
            days_left = (driver.license_expiry_date - today).days
            
            subject = f"ACTION REQUIRED: Driving License Expiry Notice - {driver.name}"
            
            if is_expired:
                time_message = f"has EXPIRED on {driver.license_expiry_date}."
                action_urgency = "IMMEDIATELY. You must not drive on active trips until your license is renewed."
            else:
                time_message = f"is scheduled to expire on {driver.license_expiry_date} (in {days_left} days)."
                action_urgency = f"before {driver.license_expiry_date} to prevent suspension of your active driving status."
                
            message_body = f"""Hello {driver.name},

This is an official notification from TransitOps Administration regarding your commercial driving license.

Your driving license details:
- License Number: {driver.license_number}
- Category: {driver.license_category}
- Expiration Date: {driver.license_expiry_date}

According to our records, your driving license {time_message}

Please renew your license and update the expiration date in the TransitOps portal {action_urgency}

If you have already renewed and updated your profile, please ignore this email.

Best regards,
TransitOps Operations Team
"""
            try:
                send_mail(
                    subject=subject,
                    message=message_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[driver.user.email],
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(
                    f"Successfully sent notification to '{driver.name}' ({driver.user.email}). Expiry: {driver.license_expiry_date}."
                ))
                sent_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"Failed to send email to '{driver.name}' ({driver.user.email}): {str(e)}"
                ))
                failed_count += 1
                
        self.stdout.write(self.style.SUCCESS(
            f"\nExpiry check complete. Sent: {sent_count}, Skipped: {skipped_count}, Failed: {failed_count}."
        ))
