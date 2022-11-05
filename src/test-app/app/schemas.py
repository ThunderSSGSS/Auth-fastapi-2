#from typing import , Optional
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import uuid



#___________________User_Schemas_____________________________#
class UserEmail(BaseModel):
    email: str