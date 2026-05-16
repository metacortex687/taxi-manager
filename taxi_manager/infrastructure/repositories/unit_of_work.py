from django.db import transaction

from taxi_manager.application.unit_of_work import IUnitOfWork  
  
  
class DjangoUnitOfWork(IUnitOfWork):  

    def transaction(self):  
        return transaction.atomic()  