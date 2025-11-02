"""
Celery tasks for asynchronous email sending in ALX Travel App

This module contains shared tasks that are executed by Celery workers
in the background, allowing the main application to remain responsive
while sending emails asynchronously.
"""
import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_booking_confirmation_email_task(self, booking_id, guest_email, guest_name, listing_title, 
                                          listing_location, check_in_date, check_out_date, total_price):
    """
    Asynchronous task to send a booking confirmation email to the guest.
    
    Args:
        booking_id: The ID of the booking
        guest_email: Email address of the guest
        guest_name: Name of the guest
        listing_title: Title of the listing
        listing_location: Location of the listing
        check_in_date: Check-in date (ISO format string)
        check_out_date: Check-out date (ISO format string)
        total_price: Total booking price
    
    Returns:
        Success message if email is sent
        
    Raises:
        Retries up to 3 times if email sending fails
    """
    try:
        subject = 'Booking Confirmation - ALX Travel App'
        
        # Create email message
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
                    <h2 style="color: #2c3e50;">Booking Confirmation</h2>
                    <p>Dear {guest_name},</p>
                    
                    <p>Thank you for booking with ALX Travel App! Your reservation has been confirmed.</p>
                    
                    <h3 style="color: #34495e; margin-top: 30px;">Booking Details</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr style="background-color: #ecf0f1;">
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Listing</td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{listing_title}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Location</td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{listing_location}</td>
                        </tr>
                        <tr style="background-color: #ecf0f1;">
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Check-in Date</td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{check_in_date}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Check-out Date</td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{check_out_date}</td>
                        </tr>
                        <tr style="background-color: #ecf0f1;">
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Total Price</td>
                            <td style="padding: 10px; border: 1px solid #ddd;">${total_price}</td>
                        </tr>
                    </table>
                    
                    <p style="margin-top: 30px;">If you have any questions, please contact our support team.</p>
                    
                    <p style="margin-top: 30px; color: #7f8c8d;">
                        Best regards,<br>
                        <strong>ALX Travel App Team</strong>
                    </p>
                </div>
            </body>
        </html>
        """
        
        # Plain text version
        plain_message = f"""
        Booking Confirmation
        
        Dear {guest_name},
        
        Thank you for booking with ALX Travel App! Your reservation has been confirmed.
        
        Booking Details:
        Listing: {listing_title}
        Location: {listing_location}
        Check-in Date: {check_in_date}
        Check-out Date: {check_out_date}
        Total Price: ${total_price}
        
        If you have any questions, please contact our support team.
        
        Best regards,
        ALX Travel App Team
        """
        
        # Send email
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [guest_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Booking confirmation email sent to {guest_email} for booking {booking_id}")
        return f"Email sent successfully to {guest_email}"
        
    except Exception as exc:
        logger.error(f"Error sending booking confirmation email: {str(exc)}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_payment_confirmation_email_task(self, booking_id, guest_email, guest_name, listing_title,
                                         listing_location, check_in_date, check_out_date, 
                                         amount, currency, payment_id, transaction_id):
    """
    Asynchronous task to send a payment confirmation email to the guest.
    
    Args:
        booking_id: The ID of the booking
        guest_email: Email address of the guest
        guest_name: Name of the guest
        listing_title: Title of the listing
        listing_location: Location of the listing
        check_in_date: Check-in date (ISO format string)
        check_out_date: Check-out date (ISO format string)
        amount: Payment amount
        currency: Payment currency (e.g., 'USD', 'ETB')
        payment_id: Payment ID from the system
        transaction_id: Transaction ID from payment gateway
    
    Returns:
        Success message if email is sent
        
    Raises:
        Retries up to 3 times if email sending fails
    """
    try:
        subject = 'Payment Confirmation - ALX Travel App'
        
        # Create email message
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
                    <h2 style="color: #27ae60;">Payment Confirmation</h2>
                    <p>Dear {guest_name},</p>
                    
                    <p>Your payment has been successfully processed. Your booking is confirmed!</p>
                    
                    <h3 style="color: #34495e; margin-top: 30px;">Payment Details</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr style="background-color: #ecf0f1;">
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Booking ID</td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{booking_id}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Listing</td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{listing_title}</td>
                        </tr>
                        <tr style="background-color: #ecf0f1;">
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Location</td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{listing_location}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Check-in</td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{check_in_date}</td>
                        </tr>
                        <tr style="background-color: #ecf0f1;">
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Check-out</td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{check_out_date}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Amount Paid</td>
                            <td style="padding: 10px; border: 1px solid #ddd; color: #27ae60; font-weight: bold;">
                                {amount} {currency}
                            </td>
                        </tr>
                        <tr style="background-color: #ecf0f1;">
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Payment ID</td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{payment_id}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Transaction ID</td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{transaction_id}</td>
                        </tr>
                    </table>
                    
                    <p style="margin-top: 30px;">If you have any questions, please contact our support team.</p>
                    
                    <p style="margin-top: 30px; color: #7f8c8d;">
                        Best regards,<br>
                        <strong>ALX Travel App Team</strong>
                    </p>
                </div>
            </body>
        </html>
        """
        
        # Plain text version
        plain_message = f"""
        Payment Confirmation
        
        Dear {guest_name},
        
        Your payment has been successfully processed. Your booking is confirmed!
        
        Payment Details:
        Booking ID: {booking_id}
        Listing: {listing_title}
        Location: {listing_location}
        Check-in: {check_in_date}
        Check-out: {check_out_date}
        Amount Paid: {amount} {currency}
        Payment ID: {payment_id}
        Transaction ID: {transaction_id}
        
        If you have any questions, please contact our support team.
        
        Best regards,
        ALX Travel App Team
        """
        
        # Send email
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [guest_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Payment confirmation email sent to {guest_email} for booking {booking_id}")
        return f"Email sent successfully to {guest_email}"
        
    except Exception as exc:
        logger.error(f"Error sending payment confirmation email: {str(exc)}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_payment_failure_email_task(self, guest_email, guest_name, listing_title, booking_id, error_message):
    """
    Asynchronous task to send a payment failure notification email.
    
    Args:
        guest_email: Email address of the guest
        guest_name: Name of the guest
        listing_title: Title of the listing
        booking_id: The ID of the booking
        error_message: Error message explaining why payment failed
    
    Returns:
        Success message if email is sent
        
    Raises:
        Retries up to 3 times if email sending fails
    """
    try:
        subject = 'Payment Failed - ALX Travel App'
        
        # Create email message
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
                    <h2 style="color: #e74c3c;">Payment Failed</h2>
                    <p>Dear {guest_name},</p>
                    
                    <p>Unfortunately, your payment could not be processed. Please try again or contact support for assistance.</p>
                    
                    <h3 style="color: #34495e; margin-top: 30px;">Booking Information</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr style="background-color: #ecf0f1;">
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Booking ID</td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{booking_id}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Listing</td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{listing_title}</td>
                        </tr>
                        <tr style="background-color: #ecf0f1;">
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Error</td>
                            <td style="padding: 10px; border: 1px solid #ddd; color: #e74c3c;">{error_message}</td>
                        </tr>
                    </table>
                    
                    <p style="margin-top: 30px;">Please try your payment again or contact our support team for help.</p>
                    
                    <p style="margin-top: 30px; color: #7f8c8d;">
                        Best regards,<br>
                        <strong>ALX Travel App Team</strong>
                    </p>
                </div>
            </body>
        </html>
        """
        
        # Plain text version
        plain_message = f"""
        Payment Failed
        
        Dear {guest_name},
        
        Unfortunately, your payment could not be processed. Please try again or contact support for assistance.
        
        Booking Information:
        Booking ID: {booking_id}
        Listing: {listing_title}
        Error: {error_message}
        
        Please try your payment again or contact our support team for help.
        
        Best regards,
        ALX Travel App Team
        """
        
        # Send email
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [guest_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Payment failure email sent to {guest_email} for booking {booking_id}")
        return f"Email sent successfully to {guest_email}"
        
    except Exception as exc:
        logger.error(f"Error sending payment failure email: {str(exc)}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
