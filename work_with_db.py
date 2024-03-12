from sqlalchemy.orm import Session
from sqlalchemy import insert, select
from all_models import (
    engine, Base, Owner, Employee, Company, NewOwnerCreate, CompanyCreate
    )
from fastapi import HTTPException
from hash_fun import convert_text_into_hash

__all__ = ["create_db", "clear_db", "insert_owner_in_db", "check_owner_in_db",
           "check_company_in_db", "get_company_by_owner"]


def insert_owner_in_db(new_user: NewOwnerCreate) -> Owner:
    """
    Добавление нового владельца в базу данных
    
    new_user: NewOwnerCreate
        Класс с далнными для создания нового владельца
    """

    stmt_insert = insert(Owner).values(name=new_user.name,
                                       password=new_user.password)
    stmt_select = select(Owner).where(Owner.name == new_user.name)
    
    with Session(engine) as session:
        session.execute(stmt_insert)
        session.commit()
        owner: Owner = session.scalar(stmt_select) # type: ignore
    
    return owner 
        

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
        raise HTTPException(status_code=404,
                            detail="Такого владельца нет")
    
    # Проверяем введенный пароль
    if owner_from_db.password != password_owner:
        raise HTTPException(status_code=400,
                            detail="Неверный пароль")
    
    return owner_from_db
    

def check_company_in_db(data_company: CompanyCreate, data_owner: Owner) -> Company:
    """
    Функця добавляет компанию в базу данных, тем кто прислал ее

    data_company: CompanyCreate
        Класс содержащий данные о компании

    data_owner: Owner
        Класс содержащий данные о владельце
    """

    # Вставка компании в базу данных
    stmt_insert = insert(Company).values(name=data_company.name,
                                         owner_id=data_owner.id)
    
    # Поиск компании в базе данных 
    stmt_select = select(Company).where(Company.name == data_company.name) \
                                 .where(Company.owner_id == data_owner.id)

    with Session(engine) as session:
        session.execute(stmt_insert)
        session.commit()
        company_from_db: Company = session.scalar(stmt_select) # type: ignore

    return company_from_db
    

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
    
    

if __name__ == "__main__":
    pass

