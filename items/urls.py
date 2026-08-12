from django.urls import path

from .views import (
    home,
    student_dashboard,
    add_item,
    claim,
    edit_item,
    delete_item,
    signup,
    UserLoginView,
    LogoutView,
    notifications,
    mark_notification_read,
    approve_claim,
    reject_claim,
)


urlpatterns = [

    path(
        '',
        home
    ),

    path(
        'dashboard/',
        student_dashboard,
        name='student_dashboard'
    ),

    path(
        'add/',
        add_item
    ),

    path(
        'claim/<int:id>/',
        claim,
        name='claim'
    ),

    path(
        'edit/<int:id>/',
        edit_item,
        name='edit_item'
    ),

    path(
        'delete/<int:id>/',
        delete_item,
        name='delete_item'
    ),

    path(
        'signup/',
        signup
    ),

    path(
        'login/',
        UserLoginView.as_view(),
        name='login'
    ),

    path(
        'logout/',
        LogoutView.as_view(),
        name='logout'
    ),

    path(
        'notifications/',
        notifications,
        name='notifications'
    ),

    path(
        'notifications/read/<int:id>/',
        mark_notification_read,
        name='mark_notification_read'
    ),

    path(
        'claim/<int:id>/approve/',
        approve_claim,
        name='approve_claim'
    ),

    path(
        'claim/<int:id>/reject/',
        reject_claim,
        name='reject_claim'
    ),
]