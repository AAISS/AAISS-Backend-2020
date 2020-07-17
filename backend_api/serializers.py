from django.core.validators import RegexValidator
from rest_framework import serializers

from backend_api import models, validators


def all_serializer_creator(selected_model):
    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = selected_model
            fields = '__all__'

    return Serializer


FieldOfInterestSerializer = all_serializer_creator(models.FieldOfInterest)
TeacherSerializer = all_serializer_creator(models.Teacher)
PresenterSerializer = all_serializer_creator(models.Presenter)
WorkshopSerializer = all_serializer_creator(models.Workshop)
PresentationSerializer = all_serializer_creator(models.Presentation)
MiscSerializer = all_serializer_creator(models.Misc)


class UserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    name = serializers.CharField(max_length=255, required=True)
    fields_of_interest = serializers.ListField(child=serializers.IntegerField(min_value=0), required=False)
    phone_number = serializers.CharField(max_length=12, validators=[validators.validate_all_number], required=True)
    national_code = serializers.CharField(max_length=10,
                                          validators=[RegexValidator(regex='^.{10}$', message='Length has to be 10')],
                                          required=True)


class PaymentInitSerialier(serializers.Serializer):
    email = serializers.EmailField(required=True)
    workshops = serializers.ListField(child=serializers.IntegerField(min_value=0), required=False)
    presentations = serializers.BooleanField(required=False)
