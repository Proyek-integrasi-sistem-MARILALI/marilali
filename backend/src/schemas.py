from datetime import datetime
from zoneinfo import ZoneInfo
from pydantic import BaseModel, ConfigDict
from fastapi.encoders import jsonable_encoder


def datetime_to_gmt_str(dt: datetime) -> str:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    
    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


class CustomModel(BaseModel):
    model_config = ConfigDict(
        json_encoders={datetime: datetime_to_gmt_str},
        populate_by_name=True,
        from_attributes=True,
    )
    
    def serializable_dict(self, **kwargs):
        default_dict = self.model_dump(**kwargs)
        return jsonable_encoder(default_dict)
