from pydantic import BaseModel, Field


class AddRating(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    driver_id: int = Field(..., alias='driverId', ge=0)
    client_id: int = Field(..., alias='clientId', ge=0)


class AddRatingResponse(BaseModel):
    message: str


class GetRatingResponse(BaseModel):
    rating: float = Field(..., ge=0, le=5)
    client_id: int = Field(..., alias='clientId', ge=0)
