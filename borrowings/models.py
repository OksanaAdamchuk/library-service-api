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

    def full_clean(self, exclude=None, validate_unique=True):
        super().full_clean(exclude=exclude, validate_unique=validate_unique)

        if self.actual_return_date and self.borrow_date:
            if self.actual_return_date < self.borrow_date:
                raise ValidationError(
                    "You can't return book before the date you've borrowed it."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
