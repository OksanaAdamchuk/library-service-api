from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.db import transaction

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingDetailSerializer,
    BorrowingListSerializer,
    CreateBorrowingSerializer,
    ReturnBorrowingSerializer,
)


class BorrowingListView(generics.ListCreateAPIView):
    serializer_class = BorrowingListSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self) -> serializers.Serializer:
        if self.request.method == "POST":
            return CreateBorrowingSerializer
        elif self.request.method == "GET":
            return BorrowingListSerializer

    def get_queryset(self) -> QuerySet:
        queryset = Borrowing.objects.select_related("book", "user")

        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        if self.request.user.is_staff and user_id:
            user = int(user_id)
            queryset = queryset.filter(user__id=user)

        if is_active:
            is_active = is_active.lower() == "true"
            if is_active:
                queryset = queryset.filter(actual_return_date__isnull=True)
            else:
                queryset = queryset.exclude(actual_return_date__isnull=True)

        return queryset


class BorrowingRetrieveView(generics.RetrieveAPIView):
    serializer_class = BorrowingDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        queryset = Borrowing.objects.select_related("book", "user")
        if self.request.user.is_staff:
            return queryset
        else:
            return Borrowing.objects.filter(user=self.request.user)

    def get_object(self) -> Borrowing:
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj


class ReturnBorrowingView(generics.UpdateAPIView):
    queryset = Borrowing.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ReturnBorrowingSerializer

    def update(self, request, *args, **kwargs) -> Response:
        instance = self.get_object()

        if instance.user != request.user:
            return Response({"detail": "You do not have permission to return this borrowing."}, status=status.HTTP_403_FORBIDDEN)

        if instance.actual_return_date:
            return Response({"detail": "This borrowing has already been returned."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            serializer.save()
            instance.book.inventory += 1
            instance.book.save()

        return Response({"detail": "Borrowing returned successfully."}, status=status.HTTP_200_OK)
