from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from dashboard.models import Location
from orders.models import Order, Order_Load, Trip
from .models import Captain, Credential, Trader, Vehicle


class CaptainTripListTests(APITestCase):
    endpoint = '/api/users/captains/list_captain_trips/'

    def setUp(self):
        self.origin = Location.objects.create(latitude=33.5, longitude=36.2)
        self.destination = Location.objects.create(latitude=34.7, longitude=36.7)

        self.captain = self._create_captain('captain_one')
        self.other_captain = self._create_captain('captain_two')
        self.vehicle = self._create_vehicle(self.captain)
        self.other_vehicle = self._create_vehicle(self.other_captain)

        trader_credentials = Credential.objects.create_user(
            role=Credential.Role.TRADER,
            email='trader@example.com',
            password='password123',
        )
        self.trader = Trader.objects.create(
            credentials=trader_credentials,
            ecommerce=False,
            name='Test Trader',
        )

        now = timezone.now()
        self.trip = Trip.objects.create(
            launch_datetime=now,
            arrival_datetime=now + timezone.timedelta(hours=2),
        )
        self.other_trip = Trip.objects.create(
            launch_datetime=now + timezone.timedelta(days=1),
            arrival_datetime=now + timezone.timedelta(days=1, hours=2),
        )

        first_order = self._create_order(weight=10, volume=2)
        second_order = self._create_order(weight=20, volume=3)
        other_order = self._create_order(weight=99, volume=9)
        Order_Load.objects.create(
            order=first_order,
            trip=self.trip,
            vehicle=self.vehicle,
            load_percent=50,
        )
        # A second load for the same trip verifies that the trip is not
        # duplicated while its load aggregates still include both rows.
        Order_Load.objects.create(
            order=second_order,
            trip=self.trip,
            vehicle=self.vehicle,
            load_percent=50,
        )
        Order_Load.objects.create(
            order=other_order,
            trip=self.other_trip,
            vehicle=self.other_vehicle,
            load_percent=100,
        )

    def _create_captain(self, username):
        credentials = Credential.objects.create_user(
            role=Credential.Role.CAPTAIN,
            username=username,
            password='password123',
        )
        return Captain.objects.create(
            credentials=credentials,
            accommodation=self.origin,
            permanent=False,
            name=username,
        )

    def _create_vehicle(self, captain):
        return Vehicle.objects.create(
            type=Vehicle.Type.A,
            accepted_volume=100,
            fuel_consumption_per_1km=1,
            feul_type=Vehicle.FuelType.A,
            verified=True,
            delivery=False,
            captain=captain,
        )

    def _create_order(self, weight, volume):
        return Order.objects.create(
            volume=volume,
            weight=weight,
            goods_type=Order.GoodsType.NORMAL,
            price=100,
            distance='10',
            delivery=True,
            shipment_type=Order.ShipmentType.EUV,
            trader=self.trader,
            from_location=self.origin,
            to_location=self.destination,
        )

    def _authenticate(self, captain):
        token = AccessToken.for_user(captain.credentials)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_authenticated_captain_sees_only_unique_assigned_trips(self):
        self._authenticate(self.captain)

        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.trip.id)
        self.assertEqual(response.data[0]['vehicle_ids'], [self.vehicle.id])
        self.assertEqual(response.data[0]['load_count'], 2)
        self.assertEqual(response.data[0]['total_weight'], 30.0)
        self.assertEqual(response.data[0]['total_volume'], 5.0)
        self.assertEqual(response.data[0]['origin_location_ids'], [self.origin.id])
        self.assertEqual(
            response.data[0]['destination_location_ids'],
            [self.destination.id],
        )
        self.assertNotIn(self.other_trip.id, [trip['id'] for trip in response.data])

    def test_unauthenticated_request_is_rejected(self):
        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_non_captain_is_rejected(self):
        token = AccessToken.for_user(self.trader.credentials)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_other_captain_cannot_see_first_captain_trip(self):
        self._authenticate(self.other_captain)

        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([trip['id'] for trip in response.data], [self.other_trip.id])
