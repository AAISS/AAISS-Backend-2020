from django.shortcuts import get_object_or_404
from django.core import serializers as dserializers

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status

from backend_api import models
from backend_api import serializers


class FieldOfInterestViewSet(viewsets.ViewSet):
    serializer_class = serializers.FieldOfInterestSerializer

    def list(self, request, **kwargs):
        queryset = models.FieldOfInterest.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class TeacherViewSet(viewsets.ViewSet):
    serializer_class = serializers.TeacherSerializer

    def list(self, request, **kwargs):
        queryset = models.Teacher.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = models.Teacher.objects.all()
        teacher = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(teacher)
        return Response(serializer.data)


class PresenterViewSet(viewsets.ViewSet):
    serializer_class = serializers.PresenterSerializer

    def list(self, request, **kwargs):
        queryset = models.Presenter.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = models.Presenter.objects.all()
        presenter = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(presenter)
        return Response(serializer.data)


class WorkshopViewSet(viewsets.ViewSet):
    serializer_class = serializers.WorkshopSerializer

    def list(self, request, **kwargs):
        queryset = models.Workshop.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = models.Workshop.objects.all()
        workshop = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(workshop)
        return Response(serializer.data)


class PresentationViewSet(viewsets.ViewSet):
    serializer_class = serializers.PresentationSerializer

    def list(self, request, **kwargs):
        queryset = models.Presentation.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = models.Presentation.objects.all()
        presentation = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(presentation)
        return Response(serializer.data)


class MiscViewSet(viewsets.ViewSet):
    serializer_class = serializers.MiscSerializer

    def list(self, request, **kwargs):
        queryset = models.Misc.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = models.Misc.objects.all()
        misc = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(misc)
        return Response(serializer.data)


class UserAPIView(APIView):
    serializer_class = serializers.UserSerializer

    def get(self, request):
        return Response({'GET': 'GET'})

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            foi_queryset = models.FieldOfInterest.objects.all()
            # Fields of interest array
            fois = []
            for id in serializer.validated_data.get('fields_of_interest'):
                foi = get_object_or_404(foi_queryset, pk=id)
                fois.append(foi)

            account = models.Account.objects.create_user(
                email=serializer.validated_data.get('email'),
                password='nothing'
            )

            user = models.User.objects.create(
                account=account,
                name=serializer.validated_data.get('name'),
                phone_number=serializer.validated_data.get('phone_number'),
                national_code=serializer.validated_data.get('national_code'),
            )
            user.fields_of_interest.set(fois)
            user.registered_workshops.set([])
            user.save()
            return Response({'message': 'User created'})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
