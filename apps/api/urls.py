# apps/api/urls.py

from django.urls import path
from .views import StatementAnalysisView

urlpatterns = [
    path("analyze-statement/", StatementAnalysisView.as_view(), name="analyze-statement"),
    path("analyze-statement", StatementAnalysisView.as_view()),
]
