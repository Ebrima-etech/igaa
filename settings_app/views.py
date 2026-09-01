# settings_app/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import logging

from .models import CurrencySettings, CurrencyRate, SystemSettings, SignatorySettings, Signatory
from .serializers import CurrencySettingsSerializer, SignatorySettingsSerializer, SignatorySerializer

logger = logging.getLogger(__name__)


class CurrencySettingsView(APIView):
    """
    API endpoint for managing currency settings and rates.

    GET: Retrieve user's currency settings
    POST: Save/update user's currency settings
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Save manual currency rates and settings.

        Request body:
        {
            "default_currency": "USD",
            "base_currency": "GMD",
            "mode": "manual",
            "currencies": [
                {"code": "GMD", "name": "Gambian Dalasi", "symbol": "D", "rate": 1.0},
                {"code": "USD", "name": "US Dollar", "symbol": "$", "rate": 0.017}
            ]
        }
        """
        try:
            data = request.data

            # Validate required fields exist
            if not data.get('default_currency'):
                return Response(
                    {'detail': 'default_currency is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not data.get('base_currency'):
                return Response(
                    {'detail': 'base_currency is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not data.get('currencies'):
                return Response(
                    {'detail': 'currencies is required and must be a non-empty array'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not isinstance(data['currencies'], list):
                return Response(
                    {'detail': 'currencies must be an array'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if len(data['currencies']) == 0:
                return Response(
                    {'detail': 'At least one currency is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate currency codes
            valid_codes = {'GMD', 'USD', 'GBP', 'EUR'}
            for idx, currency in enumerate(data['currencies']):
                code = currency.get('code')

                if not code:
                    return Response(
                        {'detail': f'Currency at index {idx} is missing code'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if code not in valid_codes:
                    return Response(
                        {'detail': f'Invalid currency code: {code}. Valid codes: {sorted(valid_codes)}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if not currency.get('name'):
                    return Response(
                        {'detail': f'Currency {code} is missing name'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if not currency.get('symbol'):
                    return Response(
                        {'detail': f'Currency {code} is missing symbol'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if 'rate' not in currency:
                    return Response(
                        {'detail': f'Currency {code} is missing rate'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                rate = currency.get('rate')
                if not isinstance(rate, (int, float)):
                    return Response(
                        {'detail': f'Rate for {code} must be a number, got {type(rate).__name__}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if rate < 0:
                    return Response(
                        {'detail': f'Rate for {code} must be positive, got {rate}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Use serializer to save with validation
            serializer = CurrencySettingsSerializer(
                data=data,
                context={'request': request}
            )

            if serializer.is_valid():
                settings = serializer.save()
                logger.info(
                    f'✓ Currency settings saved for user {request.user.username} '
                    f'(mode: {settings.mode}, rates: {len(settings.currencies.all())})'
                )

                return Response(
                    {
                        'success': True,
                        'message': 'Currency settings saved successfully',
                        'data': CurrencySettingsSerializer(
                            settings,
                            context={'request': request}
                        ).data
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                logger.warning(f'Validation error for user {request.user.username}: {serializer.errors}')
                return Response(
                    {'detail': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            logger.exception(f'Error saving currency settings for user {request.user.username}: {str(e)}')
            return Response(
                {'detail': f'Internal server error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get(self, request):
        """
        Retrieve user's current currency settings.

        Returns the user's saved currency settings or defaults if not yet configured.
        """
        try:
            settings = CurrencySettings.objects.get(user=request.user)
            serializer = CurrencySettingsSerializer(settings, context={'request': request})

            logger.info(f'Retrieved currency settings for user {request.user.username}')

            return Response(serializer.data, status=status.HTTP_200_OK)

        except CurrencySettings.DoesNotExist:
            # Return default settings for new users
            default_settings = {
                'default_currency': 'GMD',
                'base_currency': 'GMD',
                'mode': 'manual',
                'currencies': [
                    {'code': 'GMD', 'name': 'Gambian Dalasi', 'symbol': 'D', 'rate': 1.0},
                    {'code': 'USD', 'name': 'US Dollar', 'symbol': '$', 'rate': 0.017},
                    {'code': 'GBP', 'name': 'British Pound', 'symbol': '£', 'rate': 0.013},
                    {'code': 'EUR', 'name': 'Euro', 'symbol': '€', 'rate': 0.016},
                ]
            }

            logger.info(f'No settings found for user {request.user.username}, returning defaults')

            return Response(default_settings, status=status.HTTP_200_OK)


class CurrencyRatesListView(APIView):
    """
    API endpoint for retrieving formatted currency rates.

    GET: Get all rates for the current user
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get formatted currency rates for the authenticated user.

        Returns rates in a flat structure for easy consumption.
        """
        try:
            settings = CurrencySettings.objects.get(user=request.user)

            # Format rates as a dictionary
            rates = {}
            for rate in settings.currencies.all():
                rates[rate.code] = {
                    'name': rate.name,
                    'symbol': rate.symbol,
                    'rate': float(rate.rate)
                }

            logger.info(f'Retrieved currency rates for user {request.user.username}')

            return Response(
                {
                    'success': True,
                    'mode': settings.mode,
                    'base_currency': settings.base_currency,
                    'default_currency': settings.default_currency,
                    'rates': rates
                },
                status=status.HTTP_200_OK
            )

        except CurrencySettings.DoesNotExist:
            logger.warning(f'No currency settings found for user {request.user.username}')

            return Response(
                {
                    'success': False,
                    'detail': 'Currency settings not configured',
                    'message': 'Please configure currency settings first'
                },
                status=status.HTTP_404_NOT_FOUND
            )


class HajjPackagePriceView(APIView):
    """
    API endpoint for managing the default Hajj package price.

    GET: Retrieve the current Hajj package price
    POST: Update the Hajj package price
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve the current Hajj package price."""
        try:
            settings, _ = SystemSettings.objects.get_or_create(id=1)
            logger.info(f'Retrieved hajj package price for user {request.user.username}')
            return Response({'price': float(settings.hajj_package_price)}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(f'Error retrieving hajj package price: {str(e)}')
            return Response(
                {'detail': f'Error retrieving price: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """Update the Hajj package price."""
        try:
            price = request.data.get('price')

            if price is None:
                return Response(
                    {'detail': 'price field is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                price = float(price)
            except (ValueError, TypeError):
                return Response(
                    {'detail': f'price must be a number, got {type(price).__name__}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if price < 0:
                return Response(
                    {'detail': f'price must be positive, got {price}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            settings, _ = SystemSettings.objects.get_or_create(id=1)
            settings.hajj_package_price = price
            settings.save()

            logger.info(f'✓ Hajj package price updated to {price} by user {request.user.username}')

            return Response(
                {'price': float(settings.hajj_package_price), 'message': 'Price updated successfully'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception(f'Error updating hajj package price: {str(e)}')
            return Response(
                {'detail': f'Error updating price: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SignatoryListView(APIView):
    """
    API endpoint for listing all signatories.
    GET: Retrieve all signatories (authenticated users)
    POST: Create new signatory (admin only)
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve all signatories (authenticated users can view)"""
        try:
            signatories = Signatory.objects.all()
            serializer = SignatorySerializer(signatories, many=True)
            logger.info(f'Retrieved all signatories for user {request.user.username}')

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f'Error retrieving signatories: {str(e)}')
            return Response(
                {'detail': f'Error retrieving signatories: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """Create new signatory"""
        try:
            if not request.user.is_staff and not request.user.is_superuser:
                return Response(
                    {'detail': 'Only administrators can create signatories'},
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = SignatorySerializer(data=request.data)

            if serializer.is_valid():
                signatory = serializer.save()
                logger.info(f'✓ New signatory created by user {request.user.username}: {signatory.signatory_name}')

                return Response(
                    {
                        'success': True,
                        'message': 'Signatory created successfully',
                        'data': SignatorySerializer(signatory).data
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                logger.warning(f'Validation error creating signatory: {serializer.errors}')
                return Response(
                    {'detail': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            logger.exception(f'Error creating signatory: {str(e)}')
            return Response(
                {'detail': f'Error creating signatory: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SignatoryDetailView(APIView):
    """
    API endpoint for managing individual signatories.
    GET: Retrieve signatory details (public - for receipts)
    PUT: Update signatory (admin only)
    DELETE: Delete signatory (admin only)
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, signatory_id=None):
        """
        Retrieve signatory details.
        If no ID provided, returns active signatory (public endpoint for receipts).
        """
        try:
            if signatory_id:
                # Admin getting specific signatory
                if not request.user.is_staff and not request.user.is_superuser:
                    return Response(
                        {'detail': 'Only administrators can view signatory details'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                signatory = Signatory.objects.get(id=signatory_id)
            else:
                # Public endpoint - get active signatory
                signatory = Signatory.objects.filter(is_active=True).first()

            if not signatory:
                return Response(
                    {'detail': 'Signatory not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = SignatorySerializer(signatory)
            logger.info(f'Retrieved signatory for user {request.user.username}')

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Signatory.DoesNotExist:
            return Response(
                {'detail': 'Signatory not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception(f'Error retrieving signatory: {str(e)}')
            return Response(
                {'detail': f'Error retrieving signatory: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, signatory_id):
        """Update signatory (admin only)"""
        try:
            if not request.user.is_staff and not request.user.is_superuser:
                return Response(
                    {'detail': 'Only administrators can update signatories'},
                    status=status.HTTP_403_FORBIDDEN
                )

            signatory = Signatory.objects.get(id=signatory_id)
            serializer = SignatorySerializer(signatory, data=request.data, partial=True)

            if serializer.is_valid():
                signatory = serializer.save()
                logger.info(f'✓ Signatory updated by user {request.user.username}: {signatory.signatory_name}')

                return Response(
                    {
                        'success': True,
                        'message': 'Signatory updated successfully',
                        'data': SignatorySerializer(signatory).data
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'detail': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Signatory.DoesNotExist:
            return Response(
                {'detail': 'Signatory not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception(f'Error updating signatory: {str(e)}')
            return Response(
                {'detail': f'Error updating signatory: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, signatory_id):
        """Delete signatory (admin only)"""
        try:
            if not request.user.is_staff and not request.user.is_superuser:
                return Response(
                    {'detail': 'Only administrators can delete signatories'},
                    status=status.HTTP_403_FORBIDDEN
                )

            signatory = Signatory.objects.get(id=signatory_id)
            signatory_name = signatory.signatory_name
            signatory.delete()

            logger.info(f'✓ Signatory deleted by user {request.user.username}: {signatory_name}')

            return Response(
                {'success': True, 'message': 'Signatory deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )

        except Signatory.DoesNotExist:
            return Response(
                {'detail': 'Signatory not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception(f'Error deleting signatory: {str(e)}')
            return Response(
                {'detail': f'Error deleting signatory: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SignatorySettingsView(APIView):
    """Global signatory settings endpoint"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get global signatory settings"""
        try:
            settings, _ = SignatorySettings.objects.get_or_create(id=1)
            serializer = SignatorySettingsSerializer(settings)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(f'Error retrieving signatory settings: {str(e)}')
            return Response(
                {'detail': f'Error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """Update global signatory settings (admin only)"""
        try:
            if not request.user.is_staff and not request.user.is_superuser:
                return Response(
                    {'detail': 'Only administrators can update settings'},
                    status=status.HTTP_403_FORBIDDEN
                )

            settings, _ = SignatorySettings.objects.get_or_create(id=1)
            serializer = SignatorySettingsSerializer(settings, data=request.data, partial=True)

            if serializer.is_valid():
                settings = serializer.save()
                logger.info(f'✓ Global signatory settings updated by user {request.user.username}')

                return Response(
                    {
                        'success': True,
                        'message': 'Settings updated successfully',
                        'data': SignatorySettingsSerializer(settings).data
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'detail': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            logger.exception(f'Error updating settings: {str(e)}')
            return Response(
                {'detail': f'Error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
