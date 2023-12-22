from pydantic import BaseModel, Field


class EpisodeBase(BaseModel):
    id: int
    name: str
    broadcast_number: int = Field(serialization_alias="number")
    production_code: str = Field(
        serialization_alias="productionCode",
        examples=[
            "1ACV01",
        ],
    )
