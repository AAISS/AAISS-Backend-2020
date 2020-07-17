from django.core.validators import RegexValidator
from rest_framework import serializers

from backend_api import models, validators


class FieldOfInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FieldOfInterest
        fields = ('id', 'name')


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Teacher
        fields = '__all__'


class PresenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Presenter
        fields = '__all__'


class WorkshopSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Workshop
        fields = '__all__'


class PresentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Presentation
        fields = '__all__'


class MiscSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Misc
        fields = '__all__'


class UserSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255, required=True)
    name = serializers.CharField(max_length=255, required=True)
    fields_of_interest = serializers.ListField(child=serializers.IntegerField(min_value=0), required=False)
    phone_number = serializers.CharField(max_length=12, validators=[validators.validate_all_number], required=True)
    national_code = serializers.CharField(max_length=10,
                                          validators=[RegexValidator(regex='^.{10}$', message='Length has to be 10')],
                                          required=True)
