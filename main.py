from fastapi import FastAPI, Header, HTTPException
from work_with_db import (
    clear_db, create_db, insert_owner_in_db,
    check_owner_in_db, check_company_in_db, get_company_by_owner
    )
from all_models import (
    NewOwnerCreate, NewOwner, CompanyCreate, CompanyAnswer
    )
from uvicorn import run
from hash_fun import convert_text_into_hash
from typing import Annotated


app = FastAPI()




@app.post(path="/create/owner")
async def create_owner(owner: NewOwnerCreate) -> NewOwner:
    """
    Роут отвечает за создание нового владельца в базе данных

    owner: NewOwnerCreate
        Класс описывает какое тело запроса ожидаеться

    return: NewOwner
        Класс описывающий модель ответа в JSON
    """

    # Хешируем пароль
    owner.password = convert_text_into_hash(value=owner.password)
    result = insert_owner_in_db(new_user=owner)
    
    return NewOwner(**result.__dict__) 


@app.post(path="/company")
async def add_company(new_company: CompanyCreate,
                      authorization: Annotated[str, Header()]) -> CompanyAnswer:
    """
    Роут отвечает за создание новой компании в базе данных
    и принадлежит тому владельцу, который прислал заявку

    new_company: CompanyCreate
        Класс описывает какое тело запроса ожидаеться

    authorization: str 
        Заголовок в котором находиться данные для авторизации владельца

    return: CompanyAnswer
        Класс описывающий модель ответа в JSON    
    """

    owner = check_owner_in_db(data_owner=authorization)
    company = check_company_in_db(data_company=new_company, data_owner=owner)

    return CompanyAnswer(**company.__dict__)
    

@app.get(path="/company/by/owner")
async def get_company_by_has_owner(authorization: Annotated[str, Header()]) -> CompanyAnswer:
    """
    Роут выполняет поиск компании по владельцу, который прислал заявку

     authorization: str 
        Заголовок в котором находиться данные для авторизации владельца

    return: CompanyAnswer
        Класс описывающий модель ответа в JSON
    """
    
    owner = check_owner_in_db(data_owner=authorization)
    company = get_company_by_owner(data_owner=owner)

    if company is None:
        raise HTTPException(status_code=404,
                            detail="Компании по этому владельцу нету")
    
    return CompanyAnswer(**company.__dict__)


if __name__ == "__main__":
    clear_db()
    create_db()
    run(app)