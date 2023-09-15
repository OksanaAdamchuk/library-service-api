from datetime import date
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField(
        validators=[MinValueValidator(limit_value=date.today)]
    )
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name="borrowings")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="borrowings"
    )

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name} borrows {self.book.title} till {self.expected_return_date}"

    class Meta:
        ordering = ["borrow_date"]

    @staticmethod
    def validate_date(actual_date: date, borrow_date: date, error_to_raise) -> None:
        if actual_date and borrow_date:
            if actual_date < borrow_date:
                raise error_to_raise(
                    "You can't return the book before the date you've borrowed it."
                )

    def clean(self):
        Borrowing.validate_date(
            self.actual_return_date, self.borrow_date, ValidationError
        )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
