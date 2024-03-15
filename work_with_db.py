from sqlalchemy.orm import Session
from sqlalchemy import insert, select, func
from all_models import (
    engine, Base, Owner, Employee, Company, NewOwnerCreate, CompanyCreate,
    CompanyDelete, EmployeeBase, EmployeeMany
    )
from fastapi import HTTPException
from hash_fun import convert_text_into_hash
from typing import Optional

__all__ = ["create_db", "clear_db", "insert_owner_in_db", "check_owner_in_db",
           "insert_company_in_db", "get_company_by_owner", "delete_company_from_db",
           "have_count_company_owner", "insert_employee_in_db",
           "insert_many_employee_in_db", "delete_employee_from_db"]


def have_count_company_owner(data_owner: Owner, data_company: CompanyCreate) -> None:
    """
    Функция проверяет сколько у владельца компаний, допускаеться владеть 1

    data_owner: Ownre
        Класс содержащий данные о владельце

    data_company: CompanyCreate
        Класс содержащий данные для создания компании
    """

    stmt_select = select(func.count(Company.owner_id)) \
                  .where(Company.owner_id == data_owner.id)

    with Session(engine) as session:
        count_company: int = session.scalar(stmt_select) # type: ignore

    if count_company >= 1:
        raise HTTPException(status_code=400,
                            detail="У вас уже есть компания")

def insert_owner_in_db(new_user: NewOwnerCreate) -> None:
    """
    Добавление нового владельца в базу данных
    
    new_user: NewOwnerCreate
        Класс с далнными для создания нового владельца
    """

    stmt_insert = insert(Owner).values(name=new_user.name,
                                       password=new_user.password)
    
    with Session(engine) as session:
        session.add(Owner(name=new_user.name, password=new_user.password))
        session.commit()

        
def create_db() -> None:
    "Создаем базу данных"

    Base.metadata.create_all(engine)


def clear_db() -> None:
    "Очищаем базу данны"

    Base.metadata.drop_all(engine)


def check_owner_in_db(data_owner: str) -> Owner:
    """
    Функция проверяет есть ли такой владелец в базе данных
    и проверяет пароль

    data_owner: str
        Строка где находится имя и пароль
    """

    name_ower, password = data_owner.split(":")
    password_owner = convert_text_into_hash(value=password)

    stmt_select_owner = select(Owner).where(Owner.name == name_ower)

    with Session(engine) as session:
        owner_from_db = session.scalar(stmt_select_owner)

    # Проверка на наличие владельца в бд
    if owner_from_db is None:
        raise HTTPException(status_code=401,
                            detail="Такого владельца нет")
    
    # Проверяем введенный пароль
    if owner_from_db.password != password_owner:
        raise HTTPException(status_code=403,
                            detail="Неверный пароль")
    
    return owner_from_db
    

def insert_company_in_db(data_company: CompanyCreate, data_owner: Owner) -> None:
    """
    Функця добавляет компанию в базу данных, тем кто прислал ее

    data_company: CompanyCreate
        Класс содержащий данные о компании

    data_owner: Owner
        Класс содержащий данные о владельце
    """

    # Вставка компании в базу данных

    with Session(engine) as session:
        session.add(Company(name=data_company.name, owner_id=data_owner.id))
        session.commit()

    
def get_company_by_owner(data_owner: Owner) -> Company | None:
    """
    Функция выполняет поиск компании по владельцу

    data_owner: Owner
        Класс содержащий данные о владельце
    """
    
    stmt_select = select(Company).where(Company.owner_id == data_owner.id)

    with Session(engine) as session:
        company_from_db = session.scalar(stmt_select)

    return company_from_db
    

def delete_company_from_db(data_company: CompanyDelete, data_owner: Owner) -> None:
    """
    Функция удаляет компанию из базы данных, проверяет что пришел запрос от 
    того кто владеет ей

    data_company: CompanyDelete
        Класс содержащий данные о компании

    data_owner: Owner
        Класс содержащий данные о владельце
    """
    # Проверяем что бы компания принадлежала владельцу
    stmt_select = select(Company).where(Company.name == data_company.name) \
                                 .where(Company.owner_id == data_owner.id)
    
    with Session(engine) as session:
        output = session.scalar(stmt_select)
    
        if output is None:
            raise HTTPException(status_code=400,
                                detail="Это не ваша компания") 
        session.delete(output)
        session.commit()


def insert_employee_in_db(data_owner: Owner, data_employee: EmployeeBase) -> None:
    """
    Функция добавляет сотрудника в базу данных

    data_owner: Owner
        Класс содержащий данные о владельце

    data_employee: EmployeeBase
        Класс содержащий данные о сотруднике
    """

    # Ищем id компании владельца
    stmt_select = select(Company.id).where(Company.owner_id == data_owner.id)

    with Session(engine) as session:
        company_id: int = session.scalar(stmt_select) # type: ignore
        session.add(Employee(name=data_employee.name, company_id=company_id))
        session.commit()
            

def insert_many_employee_in_db(data_owner: Owner, data_employees: EmployeeMany) -> None:
    """
    Функция выполняет множественную вставку сотрудников в бд

    data_owner: Owner
        Класс содержащий данные о владельце

    data_employees: EmployeeMany
        Класс содержащий данные о сотрудниках
    """

    # Ищем id компании владельца
    stmt_select = select(Company.id).where(Company.owner_id == data_owner.id)

    with Session(engine) as session:
        company_id: Optional[int] = session.scalar(stmt_select) 

    # Проверяем что компании существует 
    if company_id is None:
        raise HTTPException(status_code=404,
                            detail="У вас нет компании, куда можно добавить сотрудника")
        
    list_employees = [Employee(name=i_elem.name, company_id=company_id) 
                      for i_elem in data_employees.array]
    
    with Session(engine) as session:
        session.add_all(list_employees)
        session.commit()


def delete_employee_from_db(data_owner: Owner, data_employee: EmployeeBase) -> None:
    """
    Функция проверяет что работник относиться к компании владель и удаляет его

    data_owner: Owner
        Класс содержащий данные о владельце

    data_employees: EmployeeMany
        Класс содержащий данные о сотрудниках
    """

    stmt_select = select(Employee) \
                    .where(Company.owner_id.has(Company.owner_id == data_owner.id)) \
                    .where(Employee.name == data_employee.name)
    
    with Session(engine) as session:
        emp = session.scalar(stmt_select)

    if emp is None:
        raise HTTPException(status_code=404,
                            detail="У вас нет такого сотрудника")
    
    with Session(engine) as session:
        session.delete(emp)
        session.commit()
    


if __name__ == "__main__":
    pass
