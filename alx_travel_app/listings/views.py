from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from django.db.models import Q
import logging
from .models import Listing, Booking, Review, Payment
from .serializers import ListingSerializer, BookingSerializer, ReviewSerializer, PaymentSerializer
from .chapa_utils import ChapaAPIClient, create_payment_for_booking, update_payment_status
from .tasks import (
    send_payment_confirmation_email_task,
    send_payment_failure_email_task,
)

logger = logging.getLogger(__name__)


class ListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing travel property listings.
    
    Provides CRUD operations:
    - GET /api/listings/ - List all listings
    - POST /api/listings/ - Create a new listing
    - GET /api/listings/{id}/ - Retrieve a specific listing
    - PUT /api/listings/{id}/ - Update a listing
    - DELETE /api/listings/{id}/ - Delete a listing
    
    Additional actions:
    - GET /api/listings/{id}/reviews/ - Get reviews for a listing
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['location', 'is_available']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['created_at', 'price_per_night', 'title']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        """Automatically set the host to the current user when creating a listing"""
        serializer.save(host=self.request.user)

    def perform_update(self, serializer):
        """Allow only the listing host to update their listing"""
        if serializer.instance.host != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only update your own listings.")
        serializer.save()

    def perform_destroy(self, instance):
        """Allow only the listing host to delete their listing"""
        if instance.host != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only delete your own listings.")
        instance.delete()

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get all reviews for a specific listing"""
        listing = self.get_object()
        reviews = listing.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_listings(self, request):
        """Get all listings created by the current user"""
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication required.'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        listings = Listing.objects.filter(host=request.user)
        serializer = self.get_serializer(listings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def available(self, request):
        """Get all available listings"""
        listings = Listing.objects.filter(is_available=True)
        serializer = self.get_serializer(listings, many=True)
        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing travel bookings.
    
    Provides CRUD operations:
    - GET /api/bookings/ - List all bookings
    - POST /api/bookings/ - Create a new booking
    - GET /api/bookings/{id}/ - Retrieve a specific booking
    - PUT /api/bookings/{id}/ - Update a booking
    - DELETE /api/bookings/{id}/ - Delete a booking
    
    Additional actions:
    - GET /api/bookings/my_bookings/ - Get bookings made by the current user
    - PATCH /api/bookings/{id}/cancel/ - Cancel a booking
    - POST /api/bookings/{id}/initiate_payment/ - Initiate payment for booking
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'listing', 'guest']
    ordering_fields = ['created_at', 'check_in_date', 'total_price']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        """Automatically set the guest to the current user when creating a booking"""
        # Get listing from write_only field
        listing_id = self.request.data.get('listing_id')
        from .models import Listing
        listing = Listing.objects.get(listing_id=listing_id)
        
        # Calculate total_price if not provided
        total_price = serializer.validated_data.get('total_price')
        if not total_price and listing:
            from datetime import datetime
            check_in = serializer.validated_data['check_in_date']
            check_out = serializer.validated_data['check_out_date']
            days = (check_out - check_in).days
            total_price = listing.price_per_night * days
        
        booking = serializer.save(guest=self.request.user, listing=listing, total_price=total_price)
        
        # Automatically create a payment record for the booking
        create_payment_for_booking(booking)

    def get_queryset(self):
        """Filter bookings based on user role"""
        user = self.request.user
        if user.is_authenticated:
            # Users can see their own bookings and bookings for their listings
            return Booking.objects.filter(
                Q(guest=user) | Q(listing__host=user)
            ).distinct()
        return Booking.objects.none()

    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        """Get all bookings made by the current user"""
        bookings = Booking.objects.filter(guest=request.user)
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def cancel(self, request, pk=None):
        """Cancel a booking (change status to 'cancelled')"""
        booking = self.get_object()
        
        # Only guest or listing host can cancel
        if booking.guest != request.user and booking.listing.host != request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only cancel your own bookings or bookings for your listings.")
        
        # Only pending or confirmed bookings can be cancelled
        if booking.status not in ['pending', 'confirmed']:
            return Response(
                {'detail': f'Cannot cancel a {booking.status} booking.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'cancelled'
        booking.save()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def confirm(self, request, pk=None):
        """Confirm a pending booking (host only)"""
        booking = self.get_object()
        
        # Only listing host can confirm
        if booking.listing.host != request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only the listing host can confirm bookings.")
        
        # Only pending bookings can be confirmed
        if booking.status != 'pending':
            return Response(
                {'detail': f'Cannot confirm a {booking.status} booking.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'confirmed'
        booking.save()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def initiate_payment(self, request, pk=None):
        """
        Initiate payment for a booking
        
        Returns:
            - checkout_url: URL to redirect user to Chapa payment page
            - payment_id: Payment ID for reference
        """
        booking = self.get_object()
        
        # Only guest can initiate payment
        if booking.guest != request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only initiate payment for your own bookings.")
        
        # Check if payment already exists
        try:
            payment = booking.payment
        except Payment.DoesNotExist:
            payment = create_payment_for_booking(booking)
        
        # Only pending payments can be initiated
        if payment.status != 'pending':
            return Response(
                {'detail': f'Cannot initiate payment for {payment.status} payment.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Initialize Chapa API client
            chapa_client = ChapaAPIClient()
            
            # Initiate payment with Chapa
            result = chapa_client.initiate_payment(payment, booking)
            
            if result['success']:
                # Update payment reference
                update_payment_status(
                    payment,
                    'pending',
                    chapa_reference=result.get('reference')
                )
                
                return Response({
                    'success': True,
                    'checkout_url': result.get('checkout_url'),
                    'payment_id': str(payment.payment_id),
                    'amount': str(payment.amount),
                    'currency': payment.currency,
                }, status=status.HTTP_200_OK)
            else:
                error_msg = result.get('error', 'Unknown error')
                update_payment_status(
                    payment,
                    'failed',
                    error_message=error_msg
                )
                
                return Response({
                    'success': False,
                    'error': error_msg,
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except ValueError as e:
            logger.error(f"Configuration error: {str(e)}")
            return Response(
                {'error': f'Configuration error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Unexpected error during payment initiation: {str(e)}")
            return Response(
                {'error': f'Unexpected error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payments.
    
    Provides:
    - GET /api/payments/ - List all payments
    - GET /api/payments/{id}/ - Retrieve a specific payment
    - POST /api/payments/verify/ - Verify payment status with Chapa
    
    Additional actions:
    - POST /api/payments/{id}/verify_status/ - Verify specific payment status
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'booking', 'currency']
    ordering_fields = ['created_at', 'amount', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter payments based on user role"""
        user = self.request.user
        if user.is_authenticated:
            # Users can see payments for their bookings and bookings for their listings
            return Payment.objects.filter(
                Q(booking__guest=user) | Q(booking__listing__host=user)
            ).distinct()
        return Payment.objects.none()

    @action(detail=True, methods=['post'])
    def verify_status(self, request, pk=None):
        """
        Verify the status of a specific payment with Chapa
        
        Returns:
            - status: Current payment status (success, failed, pending)
            - amount: Payment amount
            - transaction_id: Chapa transaction ID
        """
        payment = self.get_object()
        
        # Only guest or host can verify payment
        if payment.booking.guest != request.user and payment.booking.listing.host != request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only verify your own payments.")
        
        if not payment.chapa_reference:
            return Response(
                {'detail': 'Payment has not been initiated yet.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            chapa_client = ChapaAPIClient()
            result = chapa_client.verify_payment(payment.chapa_reference)
            
            if result['success']:
                # Update payment status based on Chapa response
                chapa_status = result.get('status', 'pending').lower()
                
                if chapa_status == 'success':
                    update_payment_status(
                        payment,
                        'completed',
                        transaction_id=result.get('reference'),
                        payment_method=result.get('method')
                    )
                    
                    # Send confirmation email asynchronously via Celery
                    send_payment_confirmation_email_task.delay(
                        booking_id=str(payment.booking.booking_id),
                        guest_email=payment.booking.guest.email,
                        guest_name=payment.booking.guest.first_name or payment.booking.guest.username,
                        listing_title=payment.booking.listing.title,
                        listing_location=payment.booking.listing.location,
                        check_in_date=str(payment.booking.check_in_date),
                        check_out_date=str(payment.booking.check_out_date),
                        amount=str(payment.amount),
                        currency=payment.currency,
                        payment_id=str(payment.payment_id),
                        transaction_id=result.get('reference')
                    )
                    
                    return Response({
                        'success': True,
                        'status': 'completed',
                        'message': 'Payment completed successfully',
                        'amount': str(result.get('amount')),
                        'received_amount': str(result.get('received_amount')),
                        'transaction_id': result.get('reference'),
                    }, status=status.HTTP_200_OK)
                    
                elif chapa_status == 'failed':
                    update_payment_status(
                        payment,
                        'failed',
                        error_message='Payment failed on Chapa'
                    )
                    
                    # Send failure email asynchronously via Celery
                    send_payment_failure_email_task.delay(
                        guest_email=payment.booking.guest.email,
                        guest_name=payment.booking.guest.first_name or payment.booking.guest.username,
                        listing_title=payment.booking.listing.title,
                        booking_id=str(payment.booking.booking_id),
                        error_message='Your payment failed. Please try again.'
                    )
                    
                    return Response({
                        'success': False,
                        'status': 'failed',
                        'message': 'Payment failed',
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
                else:  # pending
                    return Response({
                        'success': True,
                        'status': 'pending',
                        'message': 'Payment is still pending',
                    }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': result.get('error', 'Failed to verify payment'),
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except ValueError as e:
            logger.error(f"Configuration error: {str(e)}")
            return Response(
                {'error': f'Configuration error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Unexpected error during payment verification: {str(e)}")
            return Response(
                {'error': f'Unexpected error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def verify(self, request):
        """
        Verify payment status via callback from Chapa
        
        Expected data:
        - tx_ref: Transaction reference (payment_id)
        """
        tx_ref = request.data.get('tx_ref')
        
        if not tx_ref:
            return Response(
                {'error': 'tx_ref parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            payment = Payment.objects.get(payment_id=tx_ref)
        except Payment.DoesNotExist:
            return Response(
                {'error': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            chapa_client = ChapaAPIClient()
            result = chapa_client.verify_payment(payment.chapa_reference or tx_ref)
            
            if result['success']:
                chapa_status = result.get('status', 'pending').lower()
                
                if chapa_status == 'success':
                    update_payment_status(
                        payment,
                        'completed',
                        transaction_id=result.get('reference'),
                        payment_method=result.get('method')
                    )
                    
                    # Send confirmation email asynchronously via Celery
                    send_payment_confirmation_email_task.delay(
                        booking_id=str(payment.booking.booking_id),
                        guest_email=payment.booking.guest.email,
                        guest_name=payment.booking.guest.first_name or payment.booking.guest.username,
                        listing_title=payment.booking.listing.title,
                        listing_location=payment.booking.listing.location,
                        check_in_date=str(payment.booking.check_in_date),
                        check_out_date=str(payment.booking.check_out_date),
                        amount=str(payment.amount),
                        currency=payment.currency,
                        payment_id=str(payment.payment_id),
                        transaction_id=result.get('reference')
                    )
                    
                    return Response({
                        'success': True,
                        'status': 'completed',
                        'message': 'Payment verified successfully',
                    }, status=status.HTTP_200_OK)
                    
                elif chapa_status == 'failed':
                    update_payment_status(
                        payment,
                        'failed',
                        error_message='Payment failed'
                    )
                    
                    return Response({
                        'success': False,
                        'status': 'failed',
                        'message': 'Payment failed',
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
                else:
                    return Response({
                        'success': True,
                        'status': 'pending',
                        'message': 'Payment verification pending',
                    }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': result.get('error', 'Verification failed'),
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error verifying payment: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing listing reviews.
    
    Provides CRUD operations:
    - GET /api/reviews/ - List all reviews
    - POST /api/reviews/ - Create a new review
    - GET /api/reviews/{id}/ - Retrieve a specific review
    - PUT /api/reviews/{id}/ - Update a review
    - DELETE /api/reviews/{id}/ - Delete a review
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['listing', 'reviewer', 'rating']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        """Automatically set the reviewer to the current user"""
        serializer.save(reviewer=self.request.user)

    def perform_update(self, serializer):
        """Allow only the reviewer to update their review"""
        if serializer.instance.reviewer != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only update your own reviews.")
        serializer.save()

    def perform_destroy(self, instance):
        """Allow only the reviewer to delete their review"""
        if instance.reviewer != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only delete your own reviews.")
        instance.delete()

