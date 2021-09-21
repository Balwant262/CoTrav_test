from django.db import models
from datetime import timedelta, timezone
import datetime


def one_month_from_today():
    d1 = datetime.date.today()
    return d1 + timedelta(days=30)




class Corporate_Login(models.Model):
    name = models.CharField(default=True,max_length=200)
    email = models.CharField(default=True,max_length=200)
    password = models.CharField(max_length=100)
    contact_no = models.CharField(default=True,max_length=100)
    corporate_id = models.CharField(default=True,max_length=10)
    last_login = models.DateTimeField(default=True,max_length=100)
    is_radio = models.BooleanField()
    is_local = models.BooleanField()
    is_outstation = models.BooleanField()
    is_bus = models.BooleanField()
    is_train = models.BooleanField()
    is_hotel = models.BooleanField()
    is_meal = models.BooleanField()
    is_flight = models.BooleanField()
    is_water_bottles = models.BooleanField()
    is_reverse_logistics = models.BooleanField()
    is_send_email = models.BooleanField()
    is_send_sms = models.BooleanField()
    has_billing_access = models.BooleanField()
    is_deleted = models.BooleanField()
    is_frro = models.BooleanField()
    is_visa = models.BooleanField()
    is_guesthouse = models.BooleanField()
    class Meta:
        db_table = "corporate_logins"

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.name)


class Corporate_Agent(models.Model):
    user_name = models.CharField(max_length=200)
    emp_id = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    password = models.CharField(max_length=100)
    contact_no = models.CharField(max_length=100)
    status = models.CharField(max_length=10)
    last_login = models.DateTimeField(max_length=100)
    has_radio_booking_access = models.CharField(max_length=100)
    has_local_booking_access = models.CharField(max_length=100)
    has_outstation_booking_access = models.CharField(max_length=100)
    has_bus_booking_access = models.CharField(max_length=100)
    has_train_booking_access = models.CharField(max_length=100)
    has_hotel_booking_access = models.CharField(max_length=100)
    has_flight_booking_access = models.CharField(max_length=100)
    has_meal_booking_access = models.CharField(max_length=100)
    has_water_bottles_booking_access = models.CharField(max_length=100)
    has_reverse_logistics_booking_access = models.CharField(max_length=100)
    has_billing_access = models.CharField(max_length=100)
    has_voucher_payment_access = models.CharField(max_length=100)
    has_voucher_approval_access = models.CharField(max_length=100)
    is_super_admin = models.CharField(max_length=100)
    is_relationship_manager = models.CharField(max_length=100)
    is_operation_manager = models.CharField(max_length=100)
    is_deleted = models.BooleanField()

    class Meta:
        db_table = "corporate_agents"

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)


class Corporate_Spoc_Login(models.Model):
    user_name = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=100)
    last_login = models.DateTimeField(max_length=100)
    corporate_id = models.CharField(default=True, max_length=10)
    group_id = models.CharField(default=True, max_length=10)
    subgroup_id = models.CharField(default=True, max_length=10)
    is_radio = models.BooleanField()
    is_local = models.BooleanField()
    is_outstation = models.BooleanField()
    is_bus = models.BooleanField()
    is_train = models.BooleanField()
    is_hotel = models.BooleanField()
    is_meal = models.BooleanField()
    is_flight = models.BooleanField()
    is_water_bottles = models.BooleanField()
    is_reverse_logistics = models.BooleanField()
    is_send_email = models.BooleanField()
    is_send_sms = models.BooleanField()
    is_deleted = models.BooleanField()
    is_frro = models.BooleanField()
    is_visa = models.BooleanField()
    is_guesthouse = models.BooleanField()
    class Meta:
        db_table = "corporate_spocs"

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.name)


class Corporate_Employee_Login(models.Model):
    spoc_id = models.CharField(default=True, max_length=10)
    billing_entity_id = models.CharField(default=True, max_length=10)
    corporate_id = models.CharField(default=True, max_length=10)
    employee_name = models.CharField(max_length=200)
    employee_email = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=100)
    last_login = models.DateTimeField(max_length=100)
    is_deleted = models.BooleanField()
    is_frro = models.BooleanField()
    is_visa = models.BooleanField()
    is_guesthouse = models.BooleanField()
    class Meta:
        db_table = "corporate_employees"

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.name)


class Corporate_Approves_1_Login(models.Model):
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    password = models.CharField(max_length=100)
    last_login = models.DateTimeField(max_length=100)
    corporate_id = models.CharField(default=True, max_length=10)
    subgroup_id = models.CharField(default=True, max_length=10)
    is_radio = models.BooleanField()
    is_local = models.BooleanField()
    is_outstation = models.BooleanField()
    is_bus = models.BooleanField()
    is_train = models.BooleanField()
    is_hotel = models.BooleanField()
    is_meal = models.BooleanField()
    is_flight = models.BooleanField()
    is_water_bottles = models.BooleanField()
    is_reverse_logistics = models.BooleanField()
    is_send_email = models.BooleanField()
    is_send_sms = models.BooleanField()
    is_deleted = models.BooleanField()
    is_frro = models.BooleanField()
    is_visa = models.BooleanField()
    is_guesthouse = models.BooleanField()
    class Meta:
        db_table = "corporate_subgroup_authenticater"

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.name)


class Corporate_Approves_2_Login(models.Model):
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    password = models.CharField(max_length=100)
    last_login = models.DateTimeField(max_length=100)
    corporate_id = models.CharField(default=True, max_length=10)
    group_id = models.CharField(default=True, max_length=10)
    is_radio = models.BooleanField()
    is_local = models.BooleanField()
    is_outstation = models.BooleanField()
    is_bus = models.BooleanField()
    is_train = models.BooleanField()
    is_hotel = models.BooleanField()
    is_meal = models.BooleanField()
    is_flight = models.BooleanField()
    is_water_bottles = models.BooleanField()
    is_reverse_logistics = models.BooleanField()
    is_send_email = models.BooleanField()
    is_send_sms = models.BooleanField()
    is_deleted = models.BooleanField()
    is_frro = models.BooleanField()
    is_visa = models.BooleanField()
    is_guesthouse = models.BooleanField()
    class Meta:
        db_table = "corporate_group_authenticator"

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.name)


class Corporate(models.Model):
    corporate_name = models.CharField(max_length=100)
    corporate_code = models.CharField(max_length=100)
    contact_person_name = models.CharField(max_length=100)
    contact_person_no = models.CharField(max_length=100)
    contact_person_email = models.EmailField(max_length=100)
    contact_address_line1 = models.EmailField(max_length=100)
    contact_address_line2 = models.EmailField(max_length=100)
    contact_address_line3 = models.EmailField(max_length=100)
    has_auth_level = models.BooleanField()
    has_assessment_codes = models.BooleanField()
    is_radio = models.BooleanField()
    is_local = models.BooleanField()
    is_outstation = models.BooleanField()
    is_bus = models.BooleanField()
    is_train = models.BooleanField()
    is_hotel = models.BooleanField()
    is_meal = models.BooleanField()
    is_flight = models.BooleanField()
    is_water_bottles = models.BooleanField()
    is_reverse_logistics = models.BooleanField()
    is_send_email = models.BooleanField()
    is_send_sms = models.BooleanField()
    is_guesthouse = models.BooleanField()

    class Meta:
        db_table = "corporates"


class Corporate_Login_Access_Token(models.Model):
    corporate_login_id = models.CharField(default=True, max_length=10)
    access_token = models.CharField(default=True,max_length=200)
    expiry_date = models.DateTimeField(max_length=100)
    user_agent = models.CharField(default=True, max_length=200)

    class Meta:
        db_table = "corporate_login_access_tokens"


class Corporate_Spoc_Login_Access_Token(models.Model):
    spoc_id = models.CharField(default=True, max_length=10)
    access_token = models.CharField(default=True,max_length=200)
    expiry_date = models.DateTimeField(max_length=100)
    user_agent = models.CharField(default=True, max_length=200)

    class Meta:
        db_table = "corporate_spoc_access_tokens"


class Corporate_Employee_Login_Access_Token(models.Model):
    employee_id = models.CharField(default=True, max_length=10)
    access_token = models.CharField(default=True,max_length=200)
    expiry_date = models.DateTimeField(max_length=100)
    user_agent = models.CharField(default=True, max_length=200)

    class Meta:
        db_table = "corporate_employee_access_token"

class Corporate_Approves_1_Login_Access_Token(models.Model):
    subgroup_authenticater_id = models.CharField(default=True, max_length=10)
    access_token = models.CharField(default=True,max_length=200)
    expiry_date = models.DateTimeField(max_length=100)
    user_agent = models.CharField(default=True, max_length=200)

    class Meta:
        db_table = "corporate_subgroup_authenticater_access_tokens"


class Corporate_Approves_2_Login_Access_Token(models.Model):
    group_authenticater_id = models.CharField(default=True, max_length=10)
    access_token = models.CharField(default=True,max_length=200)
    expiry_date = models.DateTimeField(max_length=100)
    user_agent = models.CharField(default=True, max_length=200)

    class Meta:
        db_table = "corporate_group_authenticater_access_tokens"


class Corporate_Agent_Login_Access_Token(models.Model):
    agent_id = models.CharField(default=True, max_length=10)
    access_token = models.CharField(default=True,max_length=200)
    expiry_date = models.DateTimeField(default=one_month_from_today)
    user_agent = models.CharField(default=True, max_length=200)

    class Meta:
        db_table = "corporate_agent_access_tokens"


class Operator_Login(models.Model):
    operator_name = models.CharField(max_length=200)
    service_type_id = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=100)
    operator_email = models.CharField(max_length=100)
    operator_contact = models.CharField(max_length=100)
    last_login = models.DateTimeField(max_length=100)
    is_radio = models.BooleanField()
    is_local = models.BooleanField()
    is_outstation = models.BooleanField()
    is_bus = models.BooleanField()
    is_train = models.BooleanField()
    is_hotel = models.BooleanField()
    is_meal = models.BooleanField()
    is_flight = models.BooleanField()
    is_water_bottles = models.BooleanField()
    is_reverse_logistics = models.BooleanField()
    is_deleted = models.BooleanField()
    class Meta:
        db_table = "operators"

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)


class Operator_Login_Access_Token(models.Model):
    operator_id = models.CharField(default=True, max_length=10)
    access_token = models.CharField(default=True,max_length=200)
    expiry_date = models.DateTimeField(max_length=100)
    user_agent = models.CharField(default=True, max_length=200)

    class Meta:
        db_table = "operator_login_access_tokens"


class Operator_Driver(models.Model):
    driver_name = models.CharField(max_length=200)
    driver_contact = models.CharField(max_length=200)
    password = models.CharField(max_length=100)
    driver_email = models.CharField(max_length=100)
    licence_no = models.CharField(max_length=100)
    last_login = models.DateTimeField(max_length=100)
    class Meta:
        db_table = "operator_drivers"

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)


class Operator_Driver_Access_Token(models.Model):
    driver_id = models.CharField(default=True, max_length=10)
    access_token = models.CharField(default=True,max_length=200)
    expiry_date = models.DateTimeField(max_length=100)
    user_agent = models.CharField(default=True, max_length=200)

    class Meta:
        db_table = "operator_driver_access_tokens"