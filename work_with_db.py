from sqlalchemy.orm import Session
from sqlalchemy import insert, select
from all_models import (
    engine, Base, Owner, Employee, Company, NewOwnerCreate
    )


__all__ = ["create_db", "clear_db", "insert_owner_in_db"]



async def insert_owner_in_db(new_user: NewOwnerCreate) -> Owner:
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


if __name__ == "__main__":
    pass

