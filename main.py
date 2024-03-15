from fastapi import FastAPI, Header, HTTPException, Response
from work_with_db import (
    clear_db, create_db, insert_owner_in_db,
    check_owner_in_db, insert_company_in_db, get_company_by_owner,
    delete_company_from_db, have_count_company_owner,
    insert_employee_in_db, insert_many_employee_in_db,
    delete_employee_from_db
    )
from all_models import (
    NewOwnerCreate, CompanyCreate, CompanyAnswer, CompanyDelete,
    EmployeeBase, EmployeeMany
    )
from uvicorn import run
from hash_fun import convert_text_into_hash
from typing import Annotated, Dict


app = FastAPI()




@app.post(path="/create/owner")
async def create_owner(owner: NewOwnerCreate) -> Response:
    """
    Роут отвечает за создание нового владельца в базе данных

    owner: NewOwnerCreate
        Класс описывает какое тело запроса ожидаеться

    return: NewOwner
        Класс описывающий модель ответа в JSON
    """

    # Хешируем пароль
    owner.password = convert_text_into_hash(value=owner.password)
    insert_owner_in_db(new_user=owner)
    
    return Response(status_code=201)


@app.post(path="/company")
async def add_company(new_company: CompanyCreate,
                      authorization: Annotated[str, Header()]) -> Response:
    """
    Роут отвечает за создание новой компании в базе данных
    и принадлежит тому владельцу, который прислал заявку

    new_company: CompanyCreate
        Класс описывает какое тело запроса ожидаеться

    authorization: str 
        Заголовок в котором находится данные для авторизации владельца

    return: CompanyAnswer
        Класс описывающий модель ответа в JSON    
    """

    owner = check_owner_in_db(data_owner=authorization)
    have_count_company_owner(data_owner=owner, data_company=new_company)
    insert_company_in_db(data_company=new_company, data_owner=owner)

    return Response(status_code=201)
    

@app.delete(path="/company")
async def delete_company(has_company: CompanyDelete,
                         authorization: Annotated[str, Header()]) -> Response:
    """
    Роут отвечает за удаление компании из базы данных того владельца
    кто ее прислал

    has_company: CompanyDelete
        Класс описывает какое тело запроса ожидаеться

    authorization: str 
        Заголовок в котором находится данные для авторизации владельца
    """

    owner = check_owner_in_db(data_owner=authorization)
    delete_company_from_db(data_company=has_company, data_owner=owner)

    return Response(status_code=201)


@app.get(path="/company/by/owner")
async def get_company_by_has_owner(authorization: Annotated[str, Header()]) -> CompanyAnswer:
    """
    Роут выполняет поиск компании по владельцу, который прислал заявку

     authorization: str 
        Заголовок в котором находится данные для авторизации владельца

    return: CompanyAnswer
        Класс описывающий модель ответа в JSON
    """
    
    owner = check_owner_in_db(data_owner=authorization)
    company = get_company_by_owner(data_owner=owner)

    if company is None:
        raise HTTPException(status_code=404,
                            detail="Компании по этому владельцу нету")
    
    return CompanyAnswer(**company.__dict__)


@app.post(path="/create/employee")
async def add_employee(new_employee: EmployeeBase,
                        authorization: Annotated[str, Header()]) -> Response:
    """
    Роут выполняет в ед. числе вставку сотрудника в базу данных
    
    new_employee: EmployeeBase
        Класс описывающий какое тело запроса ожидается

    authorization: str 
        Заголовок в котором находится данные для авторизации владельца
    """

    owner = check_owner_in_db(data_owner=authorization)
    insert_employee_in_db(data_owner=owner, data_employee=new_employee)

    return Response(status_code=201)


@app.post(path="/create/employees")
async def add_employees(employees: EmployeeMany,
                        authorization: Annotated[str, Header()]) -> Response:
    """
    Роут отвечает за множественнуое добавление сотрудников в базу данных
    
    employees: EmployeeMany
        Класс описывающий какое тело запроса ожидается

    authorization: str 
        Заголовок в котором находится данные для авторизации владельца
    """

    owner = check_owner_in_db(data_owner=authorization)
    insert_many_employee_in_db(data_owner=owner, data_employees=employees)

    return Response(status_code=201)


@app.delete(path="/create/employee")
async def delete_employee(employee: EmployeeBase,
                          authorization: Annotated[str, Header()]) -> Response:
    """
    Роут отвечает за удаление сотрудника из база данных

    employee: EmployeeBase
        Класс описывающий как тело запроса ожидается

    authorization: str
        Заголовок в котором находится данные для авторизации владельца
    """

    owner = check_owner_in_db(data_owner=authorization)
    delete_employee_from_db(data_owner=owner, data_employee=employee)

    return Response(status_code=201)


if __name__ == "__main__":
    clear_db()
    create_db()
    run(app)