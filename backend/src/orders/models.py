from django.db import models

from tools.models import TimeStampedModel

# Create your models here.
class Order(TimeStampedModel):
    volume = models.FloatField(null=False, blank=False)
    weight = models.FloatField(null=False, blank=False)
    class GoodsType(models.TextChoices):
        LIQUID = "liquid", "Liquid"
        NEED_REFRIGERATION = "need_refrigeration", "Need_Refrigeration"
        NORMAL_BREAKABLE = "normal_breakable", "Normal_Breakable"
        NORMAL = "normal", "Normal"
    goods_type = models.CharField(
        max_length=20,
        choices=GoodsType.choices,
        default=GoodsType.NORMAL,
        null=False,
        blank=False
    )
    price = models.FloatField(null=False, blank=False)
    distance = models.CharField(max_length=40, null=False, blank=False)
    delivery = models.BooleanField(default=False,null=False, blank=False)
    class ShipmentType(models.TextChoices):
        # shipment enum:
        LTL = 'LTL', 'ltl'
        EUV = 'EUV', 'euv'
        SPECIAL_SHIPMENT = 'Special_Shipment', 'special_shipment'
        # delivery enum:
        FROM_BRANCH = 'From_Branch', 'from_branch'
        TO_BRANCH = 'To_Branch', 'to_branch'
        ecommerce_delivery = 'Ecommerce_Delivery', 'ecommerce_delivery'
    shipment_type = models.CharField(
        max_length=20,
        choices=ShipmentType.choices,
        null=False,
        blank=False
    )
    trader = models.ForeignKey(
        'users.Trader',
        on_delete=models.CASCADE,
        related_name='orders',
        null=False,
        blank=False
    )
    destination = models.ForeignKey(
        'dashboard.Location',
        on_delete=models.CASCADE,
        related_name='orders',
        null=False,
        blank=False
    )
    from_branch = models.ForeignKey(
        'dashboard.Branch',
        on_delete=models.CASCADE,
        related_name="orders",
        null=False,
        blank=False
    )
    special_shipment = models.ForeignKey(
        "Special_Shipment",
        on_delete=models.CASCADE,
        related_name='orders',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'orders'
        constraints = [
            models.CheckConstraint(
                name = 'volume_must_be_more_than_or_equal_0',
                condition = models.Q(volume__gte=0)
            ),
            models.CheckConstraint(
                name = 'weight_must_be_more_than_or_equal_0',
                condition = models.Q(weight__gte=0)
            ),
            models.CheckConstraint(
                name = 'price_must_be_more_than_or_equal_0',
                condition = models.Q(price__gte=0)
            )
        ]

class Special_Shipment(TimeStampedModel):
    title = models.CharField(max_length=40, unique=True, null=False, blank=False)
    price = models.FloatField(null=False, blank=False)
    
    class Meta:
        db_table = 'special_shipments'

class Trip(TimeStampedModel):
    arrival_datetime = models.DateTimeField(null=False, blank=False)
    launch_datetime = models.DateTimeField(null=False, blank=False)
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        LAUNCHED = 'launched', 'Launched'
        DELIVERED = 'delivered', 'Delivered'
        CANCELED = 'canceled', 'Canceled'
        COMPLETE = 'complete', 'Complete'
        COMPLETE_WITH_DAMAGE = 'complete_with_damage', 'Complete_With_Damage'
        # delivery:
        RECEIVED_GOODS = 'received_goods', 'Received_Goods'
        DELIVERED_GOODS = 'Delivered_Goods', 'delivered_goods'
    status = models.CharField(
        max_length=22,
        choices=Status.choices,
        default=Status.PENDING,
        null=False,
        blank=False
    )

    class Meta:
        db_table = 'trips'

class Order_Load(TimeStampedModel):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_loads',
        null=False,
        blank=False
    )
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='order_loads',
        null=False,
        blank=False
    )
    vehicle = models.ForeignKey(
        'users.Vehicle',
        on_delete=models.CASCADE,
        related_name='order_loads',
        null=False,
        blank=False
    )
    load_percent = models.FloatField(null=False, blank=False)

    class Meta:
        db_table = 'order_loads'


