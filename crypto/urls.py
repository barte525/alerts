"""crypto URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from crypto.views.AlertView import AlertView, outher_check_alert, change_on_email_for_user
from crypto.views.ReportView import ReportView


urlpatterns = [
    path('api/alert/', AlertView.as_view()),
    path('api/check_alert/', outher_check_alert),
    path('api/report/', ReportView.as_view()),
    path('api/update-on-email/', change_on_email_for_user)
]
