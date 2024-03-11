from fastapi import FastAPI
from work_with_db import (
    clear_db, create_db, insert_owner_in_db
    )
from all_models import NewOwnerCreate, NewOwner
from uvicorn import run


app = FastAPI()




@app.post(path="/create/owner")
async def create_owner(owner: NewOwnerCreate) -> NewOwner:
    """
    Роут отвечает за создание нового владельца в базе данных

    owner: NewOwnerCreate
        То какой тело запроса ожидаеться

    return: NewOwner
        Модель ответа
    """

    result = await insert_owner_in_db(new_user=owner)
    
    answer = NewOwner(**result.__dict__) # type: ignore

    return answer


# @app


if __name__ == "__main__":
    clear_db()
    create_db()
    run(app)