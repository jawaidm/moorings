from __future__ import unicode_literals

from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from datetime import date, time
from taggit.managers import TaggableManager

# Create your models here.

class CustomerContact(models.Model):
    name = models.CharField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=255)
    description = models.TextField()
    opening_hours = models.TextField()
    other_services = models.TextField()


class Park(models.Model):
    name = models.CharField(max_length=255)
    district = models.ForeignKey('District', null=True, on_delete=models.PROTECT)
    ratis_id = models.IntegerField(default=-1)
    entry_fee_required = models.BooleanField(default=True)

    def __str__(self):
        return '{} - {}'.format(self.name, self.district)

    class Meta:
        unique_together = (('name',),)


class PromoArea(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Contact(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=12)

    def __str__(self):
        return "{}: {}".format(self.name, self.phone_number)

class Campground(models.Model):
    CAMPGROUND_TYPE_CHOICES = (
        (0, 'Campground: no bookings'),
        (1, 'Campground: book online'),
        (2, 'Campground: book by phone'),
        (3, 'Other accomodation'),
        (4, 'Not Published')
    )

    SITE_TYPE_CHOICES = (
        (0, 'Unnumbered Site'),
        (1, 'Numbered site')
    )

    name = models.CharField(max_length=255, null=True)
    park = models.ForeignKey('Park', on_delete=models.PROTECT)
    ratis_id = models.IntegerField(default=-1)
    contact = models.ForeignKey('Contact', on_delete=models.PROTECT, blank=True, null=True)
    campground_type = models.SmallIntegerField(choices=CAMPGROUND_TYPE_CHOICES, default=0)
    promo_area = models.ForeignKey('PromoArea', on_delete=models.PROTECT, null=True)
    site_type = models.SmallIntegerField(choices=SITE_TYPE_CHOICES, default=0)
    address = JSONField(null=True)
    features = models.ManyToManyField('Feature')
    description = models.TextField(blank=True, null=True)
    area_activities = models.TextField(blank=True, null=True)
    # Tags for communications methods available and access type
    tags = TaggableManager()
    driving_directions = models.TextField(blank=True, null=True)
    fees = models.TextField(blank=True, null=True)
    othertransport = models.TextField(blank=True, null=True)
    key = models.CharField(max_length=255, blank=True, null=True)
    customer_contact = models.ForeignKey('CustomerContact', null=True, on_delete=models.PROTECT)
    
    wkb_geometry = models.PointField(srid=4326, blank=True, null=True)
    bookable_per_site = models.BooleanField(default=False)
    dog_permitted = models.BooleanField(default=False)
    check_in = models.TimeField(default=time(14))
    check_out = models.TimeField(default=time(10))

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('name', 'park'),)


class BookingRange(models.Model):
    BOOKING_RANGE_CHOICES = (
        (0, 'Open'),
        (1, 'Closed due to natural disaster'),
        (2, 'Closed for maintenance'),
    )

    campground = models.ForeignKey('Campground', on_delete=models.PROTECT)
    
    # minimum/maximum consecutive days allowed for a booking
    min_days = models.SmallIntegerField(default=1)
    max_days = models.SmallIntegerField(default=28)
    # minimum/maximum number of campsites allowed for a booking
    min_sites = models.SmallIntegerField(default=1)
    max_sites = models.SmallIntegerField(default=12)
    # Minimum and Maximum days that a booking can be made before arrival
    min_dba = models.SmallIntegerField(default=0)
    max_dba = models.SmallIntegerField(default=180)
    
    status = models.SmallIntegerField(choices=BOOKING_RANGE_CHOICES, default=0)
    details = models.TextField()
    range_start = models.DateTimeField(blank=True, null=True)
    range_end = models.DateTimeField(blank=True, null=True)


class Campsite(models.Model):
    campground = models.ForeignKey('Campground', db_index=True, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    campsite_class = models.ForeignKey('CampsiteClass', on_delete=models.PROTECT)
    wkb_geometry = models.PointField(srid=4326, blank=True, null=True)
    features = models.ManyToManyField('Feature')

    def __str__(self):
        return '{} - {}'.format(self.campground, self.name)

    class Meta:
        unique_together = (('campground', 'name'),)


class Feature(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)
    image = models.ImageField(null=True)

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=255, unique=True)
    abbreviation = models.CharField(max_length=16, null=True, unique=True)
    ratis_id = models.IntegerField(default=-1)

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=255, unique=True)
    abbreviation = models.CharField(max_length=16, null=True, unique=True)
    region = models.ForeignKey('Region', on_delete=models.PROTECT)
    ratis_id = models.IntegerField(default=-1)

    def __str__(self):
        return self.name


class CampsiteClass(models.Model):
    PARKING_SPACE_CHOICES = (
        (0, 'Parking within site.'),
        (1, 'Parking for exclusive use of site occupiers next to site, but separated from tent space.'),
        (2, 'Parking for exclusive use of occupiers, short walk from tent space.'),
        (3, 'Shared parking (not allocated), short walk from tent space.')
    )

    NUMBER_VEHICLE_CHOICES = (
        (0, 'One vehicle'),
        (1, 'Two vehicles'),
        (2, 'One vehicle + small trailer'),
        (3, 'One vehicle + small trailer/large vehicle')
    )

    name = models.CharField(max_length=255, unique=True)
    camp_unit_suitability = TaggableManager()
    tents = models.SmallIntegerField(default=0)
    parking_spaces = models.SmallIntegerField(choices=PARKING_SPACE_CHOICES, default=0)
    number_vehicles = models.SmallIntegerField(choices=NUMBER_VEHICLE_CHOICES, default=0)
    min_people = models.SmallIntegerField(default=1)
    max_people = models.SmallIntegerField(default=12)
    dimensions = models.CharField(max_length=12, default='6x4')

    def __str__(self):
        return self.name


class CampsiteBooking(models.Model):
    BOOKING_TYPE_CHOICES = (
        (0, 'Reception booking'),
        (1, 'Internet booking'),
        (2, 'Black booking')
    )

    campsite = models.ForeignKey('Campsite', db_index=True, on_delete=models.PROTECT)
    date = models.DateField(db_index=True)
    booking = models.ForeignKey('Booking', on_delete=models.PROTECT, null=True)
    booking_type = models.SmallIntegerField(choices=BOOKING_TYPE_CHOICES, default=0)

    def __str__(self):
        return '{} - {}'.format(self.campsite, self.date)

    class Meta:
        unique_together = (('campsite', 'date'),)


class Rate(models.Model):
    adult = models.DecimalField(max_digits=8, decimal_places=2, default='10.00')
    concession = models.DecimalField(max_digits=8, decimal_places=2, default='6.60')
    child = models.DecimalField(max_digits=8, decimal_places=2, default='2.20')
    infant = models.DecimalField(max_digits=8, decimal_places=2, default='0')
    
    def __str__(self):
        return 'adult: ${}, concession: ${}, child: ${}, infant: ${}'.format(self.adult, self.concession, self.child, self.infant)

    class Meta:
        unique_together = (('adult', 'concession', 'child', 'infant'),)

class CampsiteRate(models.Model):
    RATE_TYPE_CHOICES = (
        (0, 'Standard'),
        (1, 'Discounted'),
    )

    PRICE_MODEL_CHOICES = (
        (0, 'Price per Person'),
        (1, 'Fixed Price'),
    )
    campsite = models.ForeignKey('Campsite', on_delete=models.PROTECT)
    rate = models.ForeignKey('Rate', on_delete=models.PROTECT)
    allow_public_holidays = models.BooleanField(default=True)
    date_start = models.DateField(default=date.today)
    date_end = models.DateField(null=True, blank=True)
    rate_type = models.SmallIntegerField(choices=RATE_TYPE_CHOICES, default=0)
    price_model = models.SmallIntegerField(choices=PRICE_MODEL_CHOICES, default=0)
   
    def get_rate(self, num_adult=0, num_concession=0, num_child=0, num_infant=0):
        return self.rate.adult*num_adult + self.rate.concession*num_concession + \
                self.rate.child*num_child + self.rate.infant*num_infant

    def __str__(self):
        return '{} - ({})'.format(self.campsite, self.rate)

    class Meta:
        unique_together = (('campsite', 'rate'),)


class Booking(models.Model):
    legacy_id = models.IntegerField(unique=True)
    legacy_name = models.CharField(max_length=255, blank=True)
    arrival = models.DateField()
    departure = models.DateField()
    details = JSONField(null=True)
    cost_total = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    campground = models.ForeignKey('Campground', null=True)
