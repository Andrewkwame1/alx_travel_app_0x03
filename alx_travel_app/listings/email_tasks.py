"""
Celery tasks for asynchronous email sending

"""
import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

logger = logging.getLogger(__name__)

# This will be used when Celery is configured
# from celery import shared_task

# For now, we'll create a non-async version that can be easily converted to Celery


def send_payment_confirmation_email(booking_obj, payment_obj):
    """
    Send payment confirmation email to the guest
    
    Args:
        booking_obj: Booking model instance
        payment_obj: Payment model instance
    """
    try:
        subject = 'Payment Confirmation - Your Travel Booking'
        
        # Prepare email context
        context = {
            'guest_name': booking_obj.guest.first_name or booking_obj.guest.username,
            'listing_title': booking_obj.listing.title,
            'listing_location': booking_obj.listing.location,
            'check_in_date': booking_obj.check_in_date,
            'check_out_date': booking_obj.check_out_date,
            'amount': payment_obj.amount,
            'currency': payment_obj.currency,
            'payment_id': payment_obj.payment_id,
            'transaction_id': payment_obj.transaction_id,
            'booking_id': booking_obj.booking_id,
        }
        
        # Create plain text and HTML email
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2>Payment Confirmation</h2>
                    <p>Dear {context['guest_name']},</p>
                    
                    <p>Your payment has been successfully processed. Here are your booking details:</p>
                    
                    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Listing:</strong> {context['listing_title']}</p>
                        <p><strong>Location:</strong> {context['listing_location']}</p>
                        <p><strong>Check-in:</strong> {context['check_in_date']}</p>
                        <p><strong>Check-out:</strong> {context['check_out_date']}</p>
                        <p><strong>Amount Paid:</strong> {context['amount']} {context['currency']}</p>
                        <p><strong>Booking Reference:</strong> {context['booking_id']}</p>
                        <p><strong>Transaction ID:</strong> {context['transaction_id']}</p>
                    </div>
                    
                    <p>Your booking is now confirmed. You can check your booking details in your account dashboard.</p>
                    
                    <p>If you have any questions, please contact the property host or our support team.</p>
                    
                    <p>Thank you for choosing our travel platform!</p>
                    
                    <hr style="margin-top: 30px; color: #ddd;">
                    <p style="font-size: 12px; color: #999;">
                        This is an automated email. Please do not reply directly to this email.
                    </p>
                </div>
            </body>
        </html>
        """
        
        plain_message = f"""
Payment Confirmation

Dear {context['guest_name']},

Your payment has been successfully processed. Here are your booking details:

Listing: {context['listing_title']}
Location: {context['listing_location']}
Check-in: {context['check_in_date']}
Check-out: {context['check_out_date']}
Amount Paid: {context['amount']} {context['currency']}
Booking Reference: {context['booking_id']}
Transaction ID: {context['transaction_id']}

Your booking is now confirmed. You can check your booking details in your account dashboard.

If you have any questions, please contact the property host or our support team.

Thank you for choosing our travel platform!
        """
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[booking_obj.guest.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Payment confirmation email sent to {booking_obj.guest.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send payment confirmation email: {str(e)}")
        return False


def send_payment_failure_email(booking_obj, payment_obj, error_message):
    """
    Send payment failure notification email to the guest
    
    Args:
        booking_obj: Booking model instance
        payment_obj: Payment model instance
        error_message: Error message describing the failure
    """
    try:
        subject = 'Payment Failed - Action Required'
        
        context = {
            'guest_name': booking_obj.guest.first_name or booking_obj.guest.username,
            'listing_title': booking_obj.listing.title,
            'amount': payment_obj.amount,
            'currency': payment_obj.currency,
            'error_message': error_message,
        }
        
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #d9534f;">Payment Failed</h2>
                    <p>Dear {context['guest_name']},</p>
                    
                    <p>Unfortunately, your payment could not be processed. Here are the details:</p>
                    
                    <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                        <p><strong>Listing:</strong> {context['listing_title']}</p>
                        <p><strong>Amount:</strong> {context['amount']} {context['currency']}</p>
                        <p><strong>Error:</strong> {context['error_message']}</p>
                    </div>
                    
                    <p>Please try again or contact your bank for more information. If the problem persists, please reach out to our support team.</p>
                    
                    <p>Thank you!</p>
                </div>
            </body>
        </html>
        """
        
        plain_message = f"""
Payment Failed - Action Required

Dear {context['guest_name']},

Unfortunately, your payment could not be processed.

Listing: {context['listing_title']}
Amount: {context['amount']} {context['currency']}
Error: {context['error_message']}

Please try again or contact your bank for more information. 
If the problem persists, please reach out to our support team.

Thank you!
        """
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[booking_obj.guest.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Payment failure email sent to {booking_obj.guest.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send payment failure email: {str(e)}")
        return False

