from django.db import models

class TimeZone(models.Model):
    code = models.CharField(max_length=64)
    utc_offset = models.IntegerField()

    @property
    def display_name(self):
        sign = "+" if self.utc_offset>=0 else "-"
        str_offset = str(self.utc_offset).zfill(2)
        return f"(UTC{sign}{str_offset}:00) {self.code}"
    
    def UTC():
        return 1 #первая запись должна быть UTC


