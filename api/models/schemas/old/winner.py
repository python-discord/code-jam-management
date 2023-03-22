from pydantic import BaseModel


class Winner(BaseModel):
    """A model representing a codejam winner."""

    user_id: int
    first_place: bool

    class Config:
        """Sets ORM mode to true so that pydantic will validate the objects returned by SQLAlchemy."""

        orm_mode = True


class WinnerResponse(Winner):
    """Response model representing a codejam winner."""

    jam_id: int
