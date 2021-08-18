import base64
import datetime
import json
from threading import Thread

from django.template.loader import render_to_string

from aaiss_backend import settings
from backend_api.email import send_simple_email
from backend_api.idpay import IdPayRequest, IDPAY_PAYMENT_DESCRIPTION, \
    IDPAY_CALL_BACK, IDPAY_STATUS_201, IDPAY_STATUS_100, IDPAY_STATUS_101, \
    IDPAY_STATUS_200, IDPAY_STATUS_10
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404, redirect
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    AllowAny
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status

from zeep import Client

from aaiss_backend.settings import env
from backend_api import models
from backend_api import serializers
from backend_api.admin import MailerThread


class FieldOfInterestViewSet(viewsets.ViewSet):
    serializer_class = serializers.FieldOfInterestSerializer

    def list(self, request, **kwargs):
        queryset = models.FieldOfInterest.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class StaffViewSet(viewsets.ViewSet):
    serializer_class = serializers.StaffSerializer

    def list(self, request, **kwargs):
        queryset = models.Staff.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class CommitteeViewSet(viewsets.ViewSet):
    serializer_class = serializers.CommitteeSerializer

    def list(self, request, **kwargs):
        queryset = models.Committee.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class TeacherViewSet(viewsets.ViewSet):
    serializer_class = serializers.TeacherSerializer

    def list(self, request, year=None, **kwargs):
        print('YEAAAR ', year)
        queryset = models.Teacher.objects.filter(year=year)
        serializer = self.serializer_class(queryset, many=True)
        for teacher_data in serializer.data:
            teacher = get_object_or_404(queryset, pk=teacher_data['id'])
            teacher_data['workshops'] = dict()
            for workshop in models.Workshop.objects.filter(teachers=teacher).all():
                teacher_data['workshops'][workshop.id] = workshop.name
        response = list(serializer.data)
        response.sort(key=lambda k: k['order'])
        return Response(response)

    def retrieve(self, request, year=None, pk=None):
        print('YEAAAR ', year)
        if year is None:
            year = datetime.datetime.now().year
        queryset = models.Teacher.objects.filter(year=year)
        teacher = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(teacher)
        workshops = []
        for workshop in models.Workshop.objects.filter(teachers=teacher).all():
            workshops.append(workshop.id)
        response = serializer.data
        response['workshops'] = workshops
        return Response(response)


class PresenterViewSet(viewsets.ViewSet):
    serializer_class = serializers.PresenterSerializer

    def list(self, request, year=None, **kwargs):
        if year is None:
            year = datetime.datetime.now().year
        queryset = models.Presenter.objects.filter(year=year)
        serializer = self.serializer_class(queryset, many=True)
        response = list(serializer.data)
        response.sort(key=lambda k: k['order'])
        return Response(response)

    def retrieve(self, request, year=None, pk=None):
        if year is None:
            year = datetime.datetime.now().year
        queryset = models.Presenter.objects.filter(year=year)
        presenter = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(presenter)
        presentations = []
        for presentation in models.Presentation.objects.filter(presenters=presenter).all():
            presentations.append(presentation.id)
        response = serializer.data
        response['presentations'] = presentations
        return Response(response)


class WorkshopViewSet(viewsets.ViewSet):
    serializer_class = serializers.WorkshopSerializer

    def list(self, request, year=None, **kwargs):
        if year is None:
            year = datetime.datetime.now().year
        queryset = models.Workshop.objects.filter(year=year)
        serializer = self.serializer_class(queryset, many=True)
        for workshop_data in serializer.data:
            workshop = get_object_or_404(queryset, pk=workshop_data['id'])
            workshop_data['is_full'] = (
                    len(models.User.objects.filter(registered_workshops=workshop).all()) >= workshop.capacity)
        return Response(serializer.data)

    def retrieve(self, request, year=None, pk=None):
        if year is None:
            year = datetime.datetime.now().year
        queryset = models.Workshop.objects.filter(year=year)
        workshop = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(workshop)
        response = dict(serializer.data)
        response['is_full'] = (
                len(models.User.objects.filter(registered_workshops=workshop).all()) >= workshop.capacity)
        return Response(response)


class PresentationViewSet(viewsets.ViewSet):
    serializer_class = serializers.PresentationSerializer

    def list(self, request, year=None, **kwargs):
        if year is None:
            year = datetime.datetime.now().year
        queryset = models.Presentation.objects.filter(year=year)
        serializer = self.serializer_class(queryset, many=True)
        total_registered_for_presentation = len(models.User.objects.filter(registered_for_presentations=True).all())
        response = list(serializer.data)
        response.append(
            {'is_full': total_registered_for_presentation >= int(models.Misc.objects.get(pk='presentation_cap').desc)})
        return Response(response)

    def retrieve(self, request, year=None, pk=None):
        if year is None:
            year = datetime.datetime.now().year
        queryset = models.Presentation.objects.filter(year=year)
        presentation = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(presentation)
        return Response(serializer.data)


class MiscViewSet(viewsets.ViewSet):
    serializer_class = serializers.MiscSerializer

    def list(self, request, year=None, **kwargs):
        if year is None:
            year = datetime.datetime.now().year
        queryset = models.Misc.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, year=None, pk=None):
        if year is None:
            year = datetime.datetime.now().year
        queryset = models.Misc.objects.all()
        misc = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(misc)
        return Response(serializer.data)


class UserAPIView(APIView):
    serializer_class = serializers.UserSerializer

    def get(self, request, pk=None, format=None):
        if request.META.get('HTTP_DAUTH') == settings.DISCORD_BOT_TOKEN:
            try:
                model_user = models.User.objects.get(account__email=(pk.lower()))
            except KeyError as e:
                return Response(status=status.HTTP_404_NOT_FOUND)
            user = dict()
            user['email'] = model_user.account.email
            user['presentation'] = model_user.registered_for_presentations
            user['name'] = model_user.name
            user['fields_of_interest'] = []
            for model_foi in model_user.fields_of_interest.all():
                foi = dict()
                foi['name'] = model_foi.name
                user['fields_of_interest'].append(foi)

            user['workshops'] = []
            for model_workshop in model_user.registered_workshops.all():
                workshop = dict()
                workshop['name'] = model_workshop.name
                user['workshops'].append(workshop)

            return Response({'user': user})
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            foi_queryset = models.FieldOfInterest.objects.all()
            # Fields of interest array
            fois = []
            if serializer.validated_data.get('fields_of_interest') is not None:
                for pkid in serializer.validated_data.get('fields_of_interest'):
                    foi = get_object_or_404(foi_queryset, pk=pkid)
                    fois.append(foi)
            try:
                account = models.Account.objects.create_user(
                    email=serializer.validated_data.get('email'),
                    password='nothing'
                )
            except IntegrityError:
                try:
                    user = models.User.objects.get(account__email=(str(serializer.validated_data.get('email')).lower()))
                except:
                    return Response(str(serializer.validated_data.get('email')).lower())
                user_workshops = []
                for workshop in user.registered_workshops.all():
                    user_workshops.append(workshop.id)

                return Response({"message": "User already exist", 'workshops': user_workshops,
                                 'presentations': user.registered_for_presentations}, status=status.HTTP_202_ACCEPTED)
            account.save()
            user = models.User.objects.create(
                account=account,
                name=serializer.validated_data.get('name'),
                phone_number=serializer.validated_data.get('phone_number'),
            )
            user.fields_of_interest.set(fois)
            user.registered_workshops.set([])
            user.save()

            return Response({'message': 'User created'})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def send_register_email(user, workshops, presentation):
    subject = 'AAISS registration'
    body = render_to_string('AAISS_Info.html',
                            {'name': user.name, 'workshops_text': ', '.join([w.name for w in workshops]),
                             'presentation': presentation})
    Thread(target=send_simple_email, args=(subject, user.account.email, body)).start()


# class PaymentAPIView(APIView):
#     serializer_class = serializers.PaymentInitSerialier
#     client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
#
#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#
#         if serializer.is_valid():
#             user = None
#             try:
#                 user = models.User.objects.get(
#                     pk=models.Account.objects.get(email=serializer.validated_data.get('email')))
#             except:
#                 return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
#             if user is None:
#                 return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
#             workshop_queryset = models.Workshop.objects.all()
#             workshops = []
#             full_workshops = []
#             presentation = False
#             total_price = 0
#             if serializer.validated_data.get('workshops') is not None:
#                 for pkid in serializer.validated_data.get('workshops'):
#                     workshop = get_object_or_404(workshop_queryset, pk=pkid)
#                     if len(models.User.objects.filter(registered_workshops=workshop).all()) >= workshop.capacity:
#                         full_workshops.append(workshop.name)
#                     else:
#                         workshops.append(workshop)
#                         total_price += workshop.cost
#             if len(full_workshops) > 0:
#                 return Response({'message': 'some are selected workshops are full', 'full_workshops': full_workshops},
#                                 status=status.HTTP_400_BAD_REQUEST)
#
#             total_registered_for_presentation = len(models.User.objects.filter(registered_for_presentations=True).all())
#             if total_registered_for_presentation >= int(models.Misc.objects.get(
#                     pk='presentation_cap').desc) and serializer.validated_data.get('presentations'):
#                 return Response({'message': 'Presentations are full'}, status=status.HTTP_400_BAD_REQUEST)
#
#             if serializer.validated_data.get('presentations'):
#                 total_price += int(get_object_or_404(models.Misc.objects.all(), pk='presentation_fee').desc)
#                 presentation = True
#
#             payment_init_data = {
#                 'MerchantID': env.str('MERCHANT_ID'),
#                 'Amount': total_price,
#                 'Description': 'ثبت نام در کارگاه ها/ارائه های رخداد AAISS',
#                 'CallbackURL': env.str('BASE_URL') + 'api/payment/'
#             }
#
#             zarin_response = self.client.service.PaymentRequest(payment_init_data['MerchantID'],
#                                                                 payment_init_data['Amount'],
#                                                                 payment_init_data['Description'], '', '',
#                                                                 payment_init_data['CallbackURL'])
#             if zarin_response.Status == 100:
#                 payment = models.Payment.objects.create(authority=str(zarin_response.Authority),
#                                                         total_price=total_price, user=user,
#                                                         presentation=presentation, is_done=False, ref_id='',
#                                                         date=datetime.datetime.now(), year=datetime.datetime.now().year)
#                 payment.workshops.set(workshops)
#                 payment.save()
#                 return Response({'message': 'https://www.zarinpal.com/pg/StartPay/' + str(zarin_response.Authority)})
#             else:
#                 return Response({'message': 'Payment Error with code: ' + str(zarin_response.Status)},
#                                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         else:
#             return Response({'message': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)
#
#     def get(self, request):
#         zarin_status = request.query_params.get('Status')
#         authority = request.query_params.get('Authority')
#         if authority is not None and status is not None:
#             try:
#                 payment = models.Payment.objects.get(pk=authority)
#             except:
#                 print('no payment found')
#                 return redirect(env.str('BASE_URL') + 'notsuccessful')
#             if zarin_status != 'OK':
#                 print('status not ok')
#                 return redirect(env.str('BASE_URL') + 'notsuccessful')
#
#             try:
#                 zarin_response = self.client.service.PaymentVerification(env.str('MERCHANT_ID'), authority,
#                                                                          payment.total_price)
#                 if zarin_response.Status == 100:
#                     payment.ref_id = zarin_response.RefID
#                     payment.save()
#                 elif zarin_response.Status == 101:
#                     response_data = dict()
#                     user_workshops = dict()
#                     for workshop in payment.user.registered_workshops.all():
#                         user_workshops[workshop.id] = workshop.name
#                     response_data['workshops'] = user_workshops
#                     response_data['presentation'] = payment.user.registered_for_presentations
#                     json_res = json.dumps(response_data)
#                     encoded = base64.encodebytes(json_res.encode('UTF-8'))
#                     return redirect(env.str('BASE_URL') + 'successful' + '?data=' + encoded.decode('UTF-8'))
#                 else:
#                     print('zarin status not success')
#                     return redirect(env.str('BASE_URL') + 'notsuccessful')
#                 new_registered_workshops = []
#                 for ws in payment.user.registered_workshops.all():
#                     new_registered_workshops.append(ws)
#                 for pws in payment.workshops.all():
#                     new_registered_workshops.append(pws)
#                 payment.user.registered_workshops.set(new_registered_workshops)
#                 payment.user.registered_for_presentations = (
#                         payment.user.registered_for_presentations or payment.presentation)
#                 payment.user.save()
#                 payment.is_done = True
#                 payment.save()
#                 response_data = dict()
#                 user_workshops = dict()
#                 for workshop in payment.user.registered_workshops.all():
#                     user_workshops[workshop.id] = workshop.name
#                 response_data['workshops'] = user_workshops
#                 response_data['presentation'] = payment.user.registered_for_presentations
#                 json_res = json.dumps(response_data)
#                 encoded = base64.encodebytes(json_res.encode('UTF-8'))
#                 send_register_email(user=payment.user, workshops=payment.workshops.all(),
#                                     presentation=payment.presentation)
#                 return redirect(env.str('BASE_URL') + 'successful' + '?data=' + encoded.decode('UTF-8'))
#             except Exception as e:
#                 print('Exception: ', e.__str__())
#                 return redirect(env.str('BASE_URL') + 'notsuccessful')
#         else:
#             print('am i a joke to you?')
#             return redirect(env.str('BASE_URL') + 'notsuccessful')


class NewPaymentAPIView(viewsets.ModelViewSet):
    serializer_class = serializers.PaymentInitSerialier
    client = IdPayRequest()

    def payment(self, request):
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
            full_workshops = []
            presentation = False
            total_price = 0
            if serializer.validated_data.get('workshops') is not None:
                for pkid in serializer.validated_data.get('workshops'):
                    workshop = get_object_or_404(workshop_queryset, pk=pkid)
                    if len(models.User.objects.filter(registered_workshops=workshop).all()) >= workshop.capacity:
                        full_workshops.append(workshop.name)
                    else:
                        workshops.append(workshop)
                        total_price += workshop.cost
            if len(full_workshops) > 0:
                return Response({'message': 'some are selected workshops are full', 'full_workshops': full_workshops},
                                status=status.HTTP_400_BAD_REQUEST)

            total_registered_for_presentation = len(models.User.objects.filter(registered_for_presentations=True).all())
            if total_registered_for_presentation >= int(models.Misc.objects.get(
                    pk='presentation_cap').desc) and serializer.validated_data.get('presentations'):
                return Response({'message': 'Presentations are full'}, status=status.HTTP_400_BAD_REQUEST)

            if serializer.validated_data.get('presentations'):
                total_price += int(get_object_or_404(models.Misc.objects.all(), pk='presentation_fee').desc)
                presentation = True

            payment = models.NewPayment.objects.create(
                total_price=total_price,
                user=user,
                presentation=presentation
            )

            result = IdPayRequest().create_payment(
                order_id=payment.pk,
                amount=int(total_price * 10),
                desc=IDPAY_PAYMENT_DESCRIPTION,
                mail=user.account.email,
                phone=user.phone_number,
                callback=IDPAY_CALL_BACK,
                name=user.name
            )
            if result['status'] == IDPAY_STATUS_201:
                payment.created_date = datetime.datetime.now()
                payment.payment_id = result['id']
                payment.payment_link = result['link']
                payment.workshops.set(workshops)
                payment.save()
                result['message'] = result['link']
                return Response(result)
            else:
                return Response({'message': 'Payment Error with code: ' + str(result['status'])},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'message': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

    def verify(self, request):
        try:
            request_body = request.data
            idPay_payment_id = request_body['id']
            order_id = request_body['order_id']
            payment = models.NewPayment.objects.get(pk=order_id)
            payment.card_number = request_body['card_no']
            payment.hashed_card_number = request_body['hashed_card_no']
            payment.payment_trackID = request_body['track_id']
            result = IdPayRequest().verify_payment(
                order_id=order_id,
                payment_id=idPay_payment_id,
            )
            result_status = result['status']

            if not (
                    any(result_status == status_code for status_code in
                        (IDPAY_STATUS_100, IDPAY_STATUS_101, IDPAY_STATUS_200))):
                payment.status = result_status
                payment.original_data = json.dumps(result)
                payment.save()
                return redirect(F'{settings.BASE_URL}?payment_status=false')

            payment.status = result_status
            payment.original_data = json.dumps(result)
            payment.verify_trackID = result['track_id']
            payment.finished_date = datetime.datetime.utcfromtimestamp(
                int(result['date']))
            payment.verified_date = datetime.datetime.utcfromtimestamp(
                int(result['verify']['date']))
            payment.save()
            new_registered_workshops = []
            for ws in payment.user.registered_workshops.all():
                new_registered_workshops.append(ws)
            for pws in payment.workshops.all():
                new_registered_workshops.append(pws)
            payment.user.registered_workshops.set(new_registered_workshops)
            payment.user.registered_for_presentations = (
                    payment.user.registered_for_presentations or payment.presentation)
            payment.user.save()
            payment.save()
            response_data = dict()
            user_workshops = dict()
            for workshop in payment.user.registered_workshops.all():
                user_workshops[workshop.id] = workshop.name
            response_data['workshops'] = user_workshops
            response_data['presentation'] = payment.user.registered_for_presentations
            json_res = json.dumps(response_data)
            encoded = base64.encodebytes(json_res.encode('UTF-8'))
            send_register_email(user=payment.user, workshops=payment.workshops.all(),
                                presentation=payment.presentation)
            return redirect(F'{settings.BASE_URL}?payment_status=true')
        except Exception as e:
            print('Exception: ', e.__str__())
            return redirect(F'{settings.BASE_URL}?payment_status=false')
