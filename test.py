from pydantic import BaseModel, ConfigDict  
from typing import Any, Dict, Optional  
class M(BaseModel):  
    settings: Optional[Dict[str, Any]] = None  
    model_config = ConfigDict(from_attributes=True)  
class Obj:  
    settings = '{"a": 1}'  
print(M.model_validate(Obj()))  
