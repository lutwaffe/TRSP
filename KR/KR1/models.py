from pydantic import BaseModel, Field, field_validator
class User(BaseModel):
    name: str
    id: int


class UserAge(BaseModel):
    name: str
    age: int

class Feedback(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    message: str = Field(min_length=10, max_length=500)

    @field_validator("message")
    @classmethod
    def check_bad_words(cls, value):
        bad_words = ["кринж", "рофл", "вайб"]

        text = value.lower()
        for word in bad_words:
            if word in text:
                raise ValueError("Ну ты и фрик, давай заканчивай")

        return value 