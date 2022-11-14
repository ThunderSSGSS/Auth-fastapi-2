#from typing import , Optional
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import uuid



#___________________User_Schemas_____________________________#
class ResponseSchema(BaseModel):
    user_id:uuid.UUID
    session_id:uuid.UUID