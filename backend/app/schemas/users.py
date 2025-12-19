from pydantic import BaseModel

class UserSchema(BaseModel):
    id: str
    username: str
    country_code: str
    rating: int = 0
    avatar_url: str | None = None
    pin_url: str | None = None

    class Config:
        orm_mode = True