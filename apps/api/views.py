# apps/api/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
import os
from django.conf import settings

from apps.statements.services import analyze_statement


class StatementAnalysisView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get("statement")
        if not file_obj:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        # Save the uploaded file to media/
        save_path = os.path.join(settings.MEDIA_ROOT, file_obj.name)
        try:
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            with open(save_path, "wb+") as destination:
                for chunk in file_obj.chunks():
                    destination.write(chunk)
            print(f"Saved successfully to {save_path}")
        except Exception as e:
            print(f"[ERROR] Could not save file: {e}")

        try:
            # Run analysis
            result = analyze_statement(save_path)
            return Response({"status": "success", "data": result}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
