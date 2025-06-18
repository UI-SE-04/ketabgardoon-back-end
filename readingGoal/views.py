from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from readingGoal.models import ReadingTarget
from readingGoal.serializers import ReadingTargetSerializer
from django.utils import timezone
from jalali_date import date2jalali

class ReadingTargetView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # show target of this year
        year = date2jalali(timezone.now()).year
        target = ReadingTarget.get_or_create_for_user_and_year(request.user, year)
        serializer = ReadingTargetSerializer(target)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # set or change target
        year = date2jalali(timezone.now()).year
        target = ReadingTarget.get_or_create_for_user_and_year(request.user, year)
        serializer = ReadingTargetSerializer(target, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
