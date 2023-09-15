import asyncio
from datetime import date
from django.core.exceptions import ValidationError

from rest_framework import serializers
from books.serializers import BookSerializer

from borrowings.models import Borrowing
from borrowings.notifications import send_notification


class BorrowingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer(many=False, read_only=True)
    user = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class CreateBorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
        )

    def validate_expected_return_date(self, value):
        if value < date.today():
            raise serializers.ValidationError("Date cannot be earlier than today.")
        return value

    def create(self, validated_data) -> Borrowing:
        book = validated_data["book"]
        if book.inventory == 0:
            raise serializers.ValidationError("Book is out of stock")

        book.inventory -= 1
        book.save()

        user = self.context["request"].user
        borrowing = Borrowing.objects.create(user=user, **validated_data)

        text = (
            f"{borrowing.user.email} borrowed "
            f"{borrowing.book.title}, {borrowing.book.author} till {borrowing.expected_return_date}"
        )

        asyncio.run(send_notification(text))

        return borrowing


class ReturnBorrowingSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(ReturnBorrowingSerializer, self).validate(attrs=attrs)
        borrow_date = self.instance.borrow_date
        Borrowing.validate_date(
            attrs["actual_return_date"], borrow_date, ValidationError
        )
        return data

    class Meta:
        model = Borrowing
        fields = ["id", "actual_return_date"]
