from pydantic import BaseModel, Field


class EpisodeBase(BaseModel):
    id: int
    name: str
    broadcast_number: int = Field(alias="number")
    production_code: str = Field(
        alias="productionCode",
        examples=[
            "1ACV01",
        ],
    )
