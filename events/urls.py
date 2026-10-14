from django.urls import path
from . import views

urlpatterns = [
    path("events/", views.event_list, name="event-list"),
    path("events/<int:event_id>/",views.event_detail,name="event-detail",),
    path("register/",views.register_user,name="register-user",),
    path("auth/login/", views.user_login, name="user-login"),
    path("registrations/",views.register_for_event,name="register-for-event"),
    path("registrations/my/",views.my_registrations,name="my-registrations"),
    path("registrations/<int:registration_id>/cancel/",views.cancel_registration,name="cancel-registration",),

]