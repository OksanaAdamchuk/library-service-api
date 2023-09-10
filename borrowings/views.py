from rest_framework import generics, serializers

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingDetailSerializer, BorrowingListSerializer, CreateBorrowingSerializer


class BorrowingListView(generics.ListCreateAPIView):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingListSerializer

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateBorrowingSerializer
        elif self.request.method == "GET":
            return BorrowingListSerializer


class BorrowingRetrieveView(generics.RetrieveAPIView):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingDetailSerializer    
