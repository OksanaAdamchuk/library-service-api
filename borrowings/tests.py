import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime
from django.core.exceptions import ValidationError

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingDetailSerializer, BorrowingListSerializer


BORROWINGS_URL = reverse("borrowings:borrowing-list-create")


class PublicBorrowingApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

        self.book = Book.objects.create(
            title="Test Title",
            author="Test Author",
            cover="Hard",
            inventory=2,
            daily_fee=2.1
        )

        self.user = get_user_model().objects.create_user(email="test@test.com", password="test123@")

        self.borrowing = Borrowing.objects.create(
            expected_return_date="2023-09-24",
            book=self.book,
            user=self.user
        )

    def test_list_borrowing_not_allowed(self) -> None:
        res = self.client.get(BORROWINGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_borrowing_not_allowed(self) -> None:
        data = {
            "expected_return_date": "2023-09-25",
            "book": self.book.id,
            "user": self.user.id,
        }
        res = self.client.post(BORROWINGS_URL, data)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_return_borrowing_not_allowed(self) -> None:
        url = reverse("borrowings:return-borrowing", args=[self.borrowing.id])
        res = self.client.patch(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_borrowing_not_allowed(self) -> None:
        url = reverse("borrowings:borrowing-detail", args=[self.borrowing.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBorrowingApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@user.com", "Testpassword123@"
        )
        self.client.force_authenticate(self.user)

        self.book1 = Book.objects.create(
            title="Test Title1",
            author="Test Author1",
            cover="Hard",
            inventory=1,
            daily_fee=2.1
        )

        self.book2 = Book.objects.create(
            title="Test Title2",
            author="Test Author2",
            cover="Hard",
            inventory=2,
            daily_fee=2.1
        )

        self.user1 = get_user_model().objects.create_user(email="test1@test.com", password="test123@")

        self.borrowing = Borrowing.objects.create(
            expected_return_date="2023-09-24",
            book=self.book1,
            user=self.user
        )

        self.borrowing1 = Borrowing.objects.create(
            expected_return_date="2023-09-25",
            book=self.book1,
            user=self.user1
        )

        self.borrowing2 = Borrowing.objects.create(
            expected_return_date="2023-09-26",
            book=self.book2,
            user=self.user
        )


    def test_str_borrowing_method(self) -> None:
        borrowing = Borrowing.objects.get(id=1)

        self.assertEqual(
            str(borrowing),
            f"{self.user.first_name} {self.user.last_name} borrows {self.book1.title} till {borrowing.expected_return_date}"
        )
        
    def test_list_borrowings_only_of_signined_user(self) -> None:
        res = self.client.get(BORROWINGS_URL)
        borrowings = Borrowing.objects.filter(user=self.user.id)
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_list_borrowings_filtering_by_is_active_status(self) -> None:
        data = {"actual_return_date": "2023-09-16"}
        url = reverse("borrowings:return-borrowing", args=[self.borrowing.id])
        self.client.patch(url, data)

        res = self.client.get(BORROWINGS_URL, {"is_active": True})
        borrowings = Borrowing.objects.filter(user=self.user.id).filter(actual_return_date__isnull=True)
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data) 

    def test_list_borrowings_filtering_by_inactive_status(self) -> None:
        data = {"actual_return_date": "2023-09-16"}
        url = reverse("borrowings:return-borrowing", args=[self.borrowing.id])
        self.client.patch(url, data)

        res = self.client.get(BORROWINGS_URL, {"is_active": False})
        borrowings = Borrowing.objects.filter(user=self.user.id).filter(actual_return_date__isnull=False)
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)      

    # def test_list_borrowings_filtering_by_user_id_not_allowed(self) -> None:
    #     res = self.client.get(BORROWINGS_URL, {"user_id": self.user1.id})
    #     borrowings = Borrowing.objects.filter(user__id=self.user1.id)
    #     serializer = BorrowingListSerializer(borrowings, many=True)
    #     print(res.data)
    #     print(serializer.data)
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(res.data, serializer.data) 

    def test_retrieve_borrowing(self) -> None:
        url = reverse("borrowings:borrowing-detail", args=[self.borrowing.id])
        res = self.client.get(url)

        serializer = BorrowingDetailSerializer(self.borrowing)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    def test_retrieve_borrowing_of_another_user_not_allowed(self) -> None:
        url = reverse("borrowings:borrowing-detail", args=[self.borrowing1.id])
        res = self.client.get(url)

        self.assertNotEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_borrowing(self) -> None:
        payload = {
            "expected_return_date": "2023-09-30",
            "book": self.book1.id,
        }
        res = self.client.post(BORROWINGS_URL, payload)
        borrowing = Borrowing.objects.get(pk=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["book"], borrowing.book.id)
        self.assertEqual(self.user.id, borrowing.user.id)
 
        expected_date = datetime.strptime(payload["expected_return_date"], "%Y-%m-%d").date()
        self.assertEqual(expected_date, getattr(borrowing, "expected_return_date"))

    def test_check_book_inventory_after_create_borrowing(self) -> None:
        payload = {
            "expected_return_date": "2023-09-30",
            "book": self.book1.id,
        }
        self.client.post(BORROWINGS_URL, payload)
        self.book1.refresh_from_db()
        
        self.assertEqual(self.book1.inventory, 0)

    def test_check_book_out_of_stock(self) -> None:
        payload = {
            "expected_return_date": "2023-09-30",
            "book": self.book1.id,
        }
        payload1 = {
            "expected_return_date": "2023-09-20",
            "book": self.book1.id,
        }
        self.client.post(BORROWINGS_URL, payload)
        self.book1.refresh_from_db()

        res = self.client.post(BORROWINGS_URL, payload1)
        self.book1.refresh_from_db()
        response_content = res.content.decode("utf-8")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
        response_data = json.loads(response_content)
        expected_message = "Book is out of stock"
        self.assertEqual(response_data, [expected_message])

    def test_create_borrowing_with_past_expected_return_date(self) -> None:
        payload = {
            "expected_return_date": "2023-09-13",
            "book": self.book1.id,
        }
        res = self.client.post(BORROWINGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_borrowing(self) -> None:
        url = reverse("borrowings:return-borrowing", args=[self.borrowing.id])
        payload = {
            "actual_return_date": "2023-09-14",
        }
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_return_borrowing_with_past_date(self) -> None:
        url = reverse("borrowings:return-borrowing", args=[self.borrowing.id])
        payload = {
            "actual_return_date": "2023-09-13",
        }
        with self.assertRaises(ValidationError) as context:
            self.client.patch(url, payload)
        expected_message = ["You can't return book before the date you've borrowed it."]

        self.assertEqual(context.exception.messages, expected_message)


class AdminUserBorrowingApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "Testpassword123@", is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.book1 = Book.objects.create(
            title="Test Title1",
            author="Test Author1",
            cover="Hard",
            inventory=1,
            daily_fee=2.1
        )

        self.book2 = Book.objects.create(
            title="Test Title2",
            author="Test Author2",
            cover="Hard",
            inventory=2,
            daily_fee=2.1
        )

        self.user1 = get_user_model().objects.create_user(email="test1@test.com", password="test123@")

        self.borrowing = Borrowing.objects.create(
            expected_return_date="2023-09-24",
            book=self.book1,
            user=self.user
        )

        self.borrowing1 = Borrowing.objects.create(
            expected_return_date="2023-09-25",
            book=self.book1,
            user=self.user1
        )

        self.borrowing2 = Borrowing.objects.create(
            expected_return_date="2023-09-26",
            book=self.book2,
            user=self.user
        )

    def test_list_borrowings_of_all_users(self) -> None:
        res = self.client.get(BORROWINGS_URL)
        borrowings = Borrowing.objects.all()
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_list_borrowings_filtering_by_is_active_status(self) -> None:
        data = {"actual_return_date": "2023-09-16"}
        url = reverse("borrowings:return-borrowing", args=[self.borrowing.id])
        self.client.patch(url, data)

        res = self.client.get(BORROWINGS_URL, {"is_active": True})
        borrowings = Borrowing.objects.filter(actual_return_date__isnull=True)
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_list_borrowings_filtering_by_user_id(self) -> None:
        res = self.client.get(BORROWINGS_URL, {"user_id": self.user1.id})
        borrowings = Borrowing.objects.filter(user__id=self.user1.id)
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data) 
