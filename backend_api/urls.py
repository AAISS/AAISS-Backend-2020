from django.urls import path, include
from rest_framework.routers import DefaultRouter

from backend_api import views


class OptionalSlashRouter(DefaultRouter):
    def __init__(self, *args, **kwargs):
        super(DefaultRouter, self).__init__(*args, **kwargs)
        self.trailing_slash = '/?'


router = OptionalSlashRouter()
router.register('foi', views.FieldOfInterestViewSet, basename='field_of_interest')

teacher_routes = [
    path(r'teacher/<int:year>/', views.TeacherViewSet.as_view({'get': 'list'})),
    path(r'teacher/<int:year>/<pk>/', views.TeacherViewSet.as_view({'get': 'retrieve'})),
]

presenter_route = [
    path(r'presenter/<int:year>/', views.PresenterViewSet.as_view({'get': 'list'})),
    path(r'presenter/<int:year>/<pk>/', views.PresenterViewSet.as_view({'get': 'retrieve'})),
]

presentation_route = [
    path(r'presentation/<int:year>/', views.PresentationViewSet.as_view({'get': 'list'})),
    path(r'presentation/<int:year>/<pk>/', views.PresentationViewSet.as_view({'get': 'retrieve'})),
]

workshop_route = [
    path(r'workshop/<int:year>/', views.WorkshopViewSet.as_view({'get': 'list'})),
    path(r'workshop/<int:year>/<pk>/', views.WorkshopViewSet.as_view({'get': 'retrieve'})),
]

misc_route = [
    path(r'misc/<int:year>/', views.MiscViewSet.as_view({'get': 'list'})),
    path(r'misc/<int:year>/<pk>/', views.MiscViewSet.as_view({'get': 'retrieve'})),
]



urlpatterns = [
    path('', include(router.urls)),
    path('', include(teacher_routes)),
    path('', include(presenter_route)),
    path('', include(presentation_route)),
    path('', include(workshop_route)),
    path('', include(misc_route)),
    path('user/', views.UserAPIView.as_view()),
    path(r'user/<pk>/', views.UserAPIView.as_view()),
    path('payment/', views.PaymentAPIView.as_view()),
]
