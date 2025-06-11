from django.db import models

from django.db import models
from custom_users.models import CustomUser
from django_jalali.db import models as jmodels
from django.utils import timezone
from jalali_date import date2jalali

class ReadingTarget(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    year = jmodels.jDateField(default=date2jalali(timezone.now()).year)
    target_books = models.PositiveIntegerField(default=0 )
    read_books = models.PositiveIntegerField(default=0 )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'year')
        verbose_name = "readingTarget"
        verbose_name_plural = "readingTargets"

    def __str__(self):
        return f"target {self.user.email} for {self.year}: {self.target_books} books"

    @property
    def progress_percentage(self):
        if self.target_books == 0:
            return 0
        return round((self.read_books / self.target_books) * 100, 2)

    @classmethod
    def get_or_create_for_user_and_year(cls, user, year=None):
        if year is None:
            year = date2jalali(timezone.now()).year
        target, created = cls.objects.get_or_create(
            user=user,
            year=year,
            defaults={'target_books': 0, 'read_books': 0}
        )
        return target
