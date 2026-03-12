from django.db import models

class TimeZone(models.Model):
    code = models.CharField(max_length=64)
    utc_offset = models.IntegerField()

    def __str__(self):
        sign = "+" if self.utc_offset>=0 else "-"
        str_offset = str(self.utc_offset).zfill(2)
        return f"(UTC{sign}{str_offset}:00) {self.code}"
    
    @property
    def display_name(self):
        return str(self)

    
    def UTC():
        return 1 #первая запись должна быть UTC


