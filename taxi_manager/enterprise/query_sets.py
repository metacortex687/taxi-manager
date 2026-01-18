from django.db import models

class EnterpriseQuerySet(models.QuerySet):
    def permited(self, user):
        return user.managed_enterprises.all()
    
        

