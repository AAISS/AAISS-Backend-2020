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
    path(r'<int:year>/teacher/', views.TeacherViewSet.as_view({'get': 'list'})),
    path(r'<int:year>/teacher/<pk>/', views.TeacherViewSet.as_view({'get': 'retrieve'})),
]

presenter_route = [
    path(r'<int:year>/presenter/', views.PresenterViewSet.as_view({'get': 'list'})),
    path(r'<int:year>/presenter/<pk>/', views.PresenterViewSet.as_view({'get': 'retrieve'})),
]

presentation_route = [
    path(r'<int:year>/presentation/', views.PresentationViewSet.as_view({'get': 'list'})),
    path(r'<int:year>/presentation/<pk>/', views.PresentationViewSet.as_view({'get': 'retrieve'})),
]

workshop_route = [
    path(r'<int:year>/workshop/', views.WorkshopViewSet.as_view({'get': 'list'})),
    path(r'<int:year>/workshop/<pk>/', views.WorkshopViewSet.as_view({'get': 'retrieve'})),
]

misc_route = [
    path(r'<int:year>/misc/', views.MiscViewSet.as_view({'get': 'list'})),
    path(r'<int:year>/misc/<pk>/', views.MiscViewSet.as_view({'get': 'retrieve'})),
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
