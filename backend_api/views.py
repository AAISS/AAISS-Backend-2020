from django.shortcuts import get_object_or_404, redirect

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status

from zeep import Client

from aaiss_backend.settings import env
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
            for pkid in serializer.validated_data.get('fields_of_interest'):
                foi = get_object_or_404(foi_queryset, pk=pkid)
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


class PaymentAPIView(APIView):
    serializer_class = serializers.PaymentInitSerialier
    client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = None
            try:
                user = models.User.objects.get(
                    pk=models.Account.objects.get(email=serializer.validated_data.get('email')))
            except:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            if user is None:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            workshop_queryset = models.Workshop.objects.all()
            workshops = []
            presentation = False
            total_price = 0
            if serializer.validated_data.get('workshops') is not None:
                for pkid in serializer.validated_data.get('workshops'):
                    workshop = get_object_or_404(workshop_queryset, pk=pkid)
                    workshops.append(workshop)
                    total_price += workshop.cost
            if serializer.validated_data.get('presentations'):
                total_price += int(get_object_or_404(models.Misc.objects.all(), pk='presentation_fee').desc)

            payment_init_data = {
                'MerchantID': env.str('MERCHANT_ID'),
                'Amount': total_price,
                'Description': 'ثبت نام در کارگاه ها/ارائه های رخداد AAISS',
                'CallbackURL': env.str('BASE_URL') + '/api/payment/'
            }

            zarin_response = self.client.service.PaymentRequest(payment_init_data['MerchantID'], payment_init_data['Amount'],
                                                           payment_init_data['Description'], '', '',
                                                           payment_init_data['CallbackURL'])
            if zarin_response.Status == 100:
                payment = models.Payment.objects.create(authority=str(zarin_response.Authority),
                                                        total_price=total_price, user=user,
                                                        presentation=presentation, is_done=False, ref_id='')
                payment.workshops.set(workshops)
                payment.save()
                return Response('https://www.zarinpal.com/pg/StartPay/' + str(zarin_response.Authority))
            else:
                return Response({'Payment Error with code: ' + zarin_response.Status},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'message': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        zarin_status = request.query_params.get('Status')
        authority = request.query_params.get('Authority')
        if authority is not None and status is not None:
            try:
                payment = models.Payment.objects.get(pk=authority)
            except:
                return Response(status=status.HTTP_404_NOT_FOUND)
            if zarin_status != 'OK':
                payment.user.account.delete()
                payment.user.account.save()
                return Response({'message': 'تراکنش ناموفق بود'}, status=status.HTTP_402_PAYMENT_REQUIRED)

            try:
                payment.user.registered_workshops.set(payment.workshops)
                payment.user.registered_for_presentations.set(payment.presentation)
                payment.user.save()
                payment.is_done = True
                payment.save()
            except:
                payment.user.account.delete()
                payment.user.account.save()
                return Response({'message': 'تراکنش ناموفق بود'}, status=status.HTTP_402_PAYMENT_REQUIRED)

            zarin_response = self.client.service.PaymentVerification(env.str('MERCHANT_ID'), authority,
                                                                     payment.total_price)
            if zarin_response.Status == 100:
                payment.ref_id = zarin_response.RedID
                payment.save()
                return redirect(env.str('BASE_URL'))
            elif zarin_response.Status == 101:
                return redirect(env.str('BASE_URL'))
            else:
                payment.user.account.delete()
                payment.user.account.save()
                return redirect(env.str('BASE_URL'))
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
