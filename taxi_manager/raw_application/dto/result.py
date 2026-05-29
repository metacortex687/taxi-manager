from dataclasses import dataclass
from enum import Enum

class ResultStatus(Enum):
    RECEIVED = "received"
    NOT_MANAGER = "not_manager"

@dataclass(frozen=True)
class Result:
    status: ResultStatus
    data: dict
    message: str = ""

    @classmethod
    def received(cls, data: dict):
        return cls(
            status=ResultStatus.RECEIVED,
            data=data,            
        ) 
    
    @classmethod
    def not_manager(cls, message):
        return cls(
            status=ResultStatus.NOT_MANAGER,
            message=message         
        ) 

    

    
    

