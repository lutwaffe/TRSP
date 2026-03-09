from fastapi import FastAPI
from fastapi.responses import FileResponse
from models import User, UserAge, Feedback
import json

app = FastAPI()

@app.get("/")
def root():
    return FileResponse("index.html")


@app.post("/calculate")
def calculate(num1: int, num2: int):
    return {"result": num1 + num2}
user = User(
    name="Имя",
    id=24
)

@app.get("/users")
def get_user():
    return user

@app.post("/user")
def check_user(user: UserAge):
    is_adult = user.age >= 18

    return {
        "name": user.name,
        "age": user.age,
        "is_adult": is_adult
    }

feedbacks = []
@app.post("/feedback")
def add_feedback(feedback: Feedback):
    data = {
        "name": feedback.name,
        "message": feedback.message
    }

    with open("feedback.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

    return {"message": f"Ну типа привет {feedback.name}"}