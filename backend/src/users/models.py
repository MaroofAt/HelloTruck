from django.db import models
from django.contrib.auth.models import BaseUserManager , AbstractBaseUser , PermissionsMixin
from django.core.exceptions import ValidationError


from tools.models import TimeStampedModel

from dashboard.models import Branch , Location
# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self , role='trader', username=None, email=None, mobile_number = None, password = None , **extra_fields):    
        if email:
            email = self.normalize_email(email.strip())
        if username:
            username = username.lower()
            username = username.strip()
        user = self.model(
            role=role,
            username=username,
            mobile_number = mobile_number,
            email = email,
            **extra_fields
        )
        user.full_clean() # here it will call self.clean() and that one will call validate_role_credential()
        user.set_password(password) # hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password , **extra_fields):
        extra_fields.setdefault('is_staff' , True)
        extra_fields.setdefault('is_superuser' , True)
        extra_fields.setdefault('is_active' , True)

        return self.create_user(role=Credential.Role.ADMIN, email=email , password=password , **extra_fields)


class Credential(AbstractBaseUser , PermissionsMixin , TimeStampedModel):
    email = email = models.EmailField(max_length=254, unique=True, null=True, blank=True)
    mobile_number = models.CharField(max_length=25, unique=True, null=True, blank=True)
    username = models.CharField(max_length=254, unique=True, null=True, blank=True)
    class Role(models.TextChoices):
        TRADER="trader", 'Trader'
        CAPTAIN='captain', 'Captain'
        SUB_ADMIN='sub_admin', 'Sub_Admin'
        ADMIN = 'admin', 'Admin'
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.TRADER
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        db_table = 'credentials'
    

    def validate_role_credential(self):
        validators = {
            Credential.Role.TRADER: (self.email or self.mobile_number),
            Credential.Role.CAPTAIN: (self.username or self.mobile_number),
            Credential.Role.SUB_ADMIN: (self.email),
            Credential.Role.ADMIN: (self.email),
        }
        if self.role not in validators:
            raise ValidationError(
                "Invalid Role"
            )
        elif not validators[self.role]:
            raise ValidationError(
                f"For {self.role}: Invalid Credentials."
            )


    def clean(self):
        super().clean()
        self.validate_role_credential()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)



class Trader(TimeStampedModel):
    
    credentials = models.OneToOneField(
        Credential,
        on_delete=models.CASCADE,
        related_name='trader'
    )
    ecommerce = models.BooleanField(null=False, blank=False)


    discounts = models.ManyToManyField(
        "Discount",
        through="Discount_Traders",
        through_fields=('trader', 'discount'),
        related_name='traders'
    )

    def clean(self):
        if self.credential.role != Credential.Role.TRADER:
            raise ValidationError(
                "Credential must have Trader role."
            )
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        db_table ='traders'
        # constraints=[
        #     models.CheckConstraint(
        #         name='one_of_email_and_mobile_number_must_not_be_null',
        #         condition= models.Q(email__isnull=False ) | models.Q(mobile_number__isnull=False)
        #     )
        # ]

class Captain(TimeStampedModel):

    credentials = models.OneToOneField(
            Credential,
            on_delete=models.CASCADE,
            related_name='captain'
        )
    accommodation = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='captains',
        null=False,
        blank=False
    )
    permanent = models.BooleanField(null=False, blank=False)

    def clean(self):
        if self.credential.role != Credential.Role.CAPTAIN:
            raise ValidationError(
                "Credential must have Captain role."
            )
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        db_table ='captains'
        # constraints=[
        #     models.CheckConstraint(
        #         name='one_of_username_and_mobile_number_must_not_be_null',
        #         condition= models.Q(username__isnull=False ) | models.Q(mobile_number__isnull=False)
        #     )
        # ]

class Sub_Admin(TimeStampedModel):

    credentials = models.OneToOneField(
            Credential,
            on_delete=models.CASCADE,
            related_name='sub_admin'
        )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='sub_admins',
        null=False,
        blank=False
    )

    def clean(self):
        if self.credential.role != Credential.Role.SUB_ADMIN:
            raise ValidationError(
                "Credential must have SubAdmin role."
            )
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        db_table= 'sub_admins'

class Discount(TimeStampedModel):
    
    class Type(models.TextChoices):
        PERCENT = "percent", 'Percent'
        FIXED = "fixed", "Fixed"
        FULL_FREE = "full_free", "Full_Free"
    type = models.CharField(
        max_length=10,
        choices=Type.choices,
        default=Type.PERCENT
    )
    validation_datetime = models.DateTimeField(null=True,blank=True)
    percent = models.FloatField(null=True, blank=True)
    fixed = models.FloatField(null=True, blank=True)


    class Meta:
        db_table= 'discounts'
        constraints=[
            models.CheckConstraint(
                name='percent_must_be_between_0_and_100',
                condition= models.Q(percent__isnull=True) | (models.Q(percent__lte=100) & models.Q(percent__gt=0))
            ),
            models.CheckConstraint(
                name='one_of_the_2_types_must_not_be_null',
                condition= models.Q(percent__isnull=False) | models.Q(fixed__isnull=False)
            ),
        ]

class Discount_Traders(TimeStampedModel):

    discount = models.ForeignKey(
        Discount,
        related_name='discounts_traders',
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )
    trader = models.ForeignKey(
        Trader,
        related_name='discounts_traders',
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )

    class Meta:
        db_table= 'discounts_traders'
        unique_together= ['discount', 'trader']

class Vehicle(TimeStampedModel):

    class Type(models.TextChoices):
        A="a"
        # TODOOOOOO
    
    type = models.CharField(
        max_length=100,
        choices=Type.choices,
        default=Type.A,
        null=False,
        blank=False
    )
    accepted_volume = models.FloatField(null=False, blank=False)
    fuel_consumption_per_1km = models.FloatField(null=False, blank=False)
    
    class FuelType(models.TextChoices):
        A='a'
        # TODOOOOOOOO
    
    feul_type = models.CharField(
        max_length=100,
        choices=FuelType.choices,
        default=FuelType.A,
        null=False,
        blank=False
    )
    verified = models.BooleanField(null=False, blank=False)
    delivery = models.BooleanField(null=False, blank=False)
    captain = models.ForeignKey(
        Captain,
        related_name="vehicle",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )

    class Meta:
        db_table= 'vehicles'