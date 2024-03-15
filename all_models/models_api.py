from pydantic import BaseModel, Field, field_validator
from .model_db import Owner, engine, Company
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException
from typing import List

__all__ = ["NewOwnerBase", "NewOwnerCreate", "CompanyBase",
           "CompanyCreate", "CompanyAnswer", "CompanyDelete",
           "EmployeeBase", "EmployeeMany"]


################################# New Owner #################################


class NewOwnerBase(BaseModel):
    "Базовая модель нового владельца"

    name: str = Field(min_length=7, 
                      max_length=50,
                      examples=["Vovan_95", "Viktoria_Per"])
        

class NewOwnerCreate(NewOwnerBase):
    "Модель для добавления в базу данных нового владельца"

    password: str = Field(min_length=11,
                          max_length=30,
                          examples=["Peshin_Ka_10"])
    

    @field_validator("name")
    @classmethod
    def check_name_in_db(cls, value: str) -> str:
        """
        Валидатор для проверки поля 'name'

         value: str
            значение которое лежит в поле 'name'
        """

        stmt = select(Owner).where(Owner.name == value)

        with Session(engine) as session:
            answer_from_db = session.scalar(stmt)

        if answer_from_db is not None:
            raise HTTPException(status_code=401,
                                detail="Такой владелец уже существует")
        
        return value


################################# Comapny #################################


class CompanyBase(BaseModel):
    "Базовая модель компании"

    name: str = Field(min_length=7,
                      max_length=50)
    

class CompanyCreate(CompanyBase):
    "Модель для добавления новой компании от владельца"
    
    @field_validator("name")
    @classmethod
    def check_name_in_db(cls, value: str) -> str:

        stmt_select = select(Company).where(Company.name == value)

        with Session(engine) as session:
            answer_from_db = session.scalar(stmt_select)

        if answer_from_db is not None:
            raise HTTPException(status_code=401,
                                detail="Такая компания уже существует")
        
        return value


class CompanyDelete(CompanyBase):
    "Модель для удаления компании"

    @field_validator("name")
    @classmethod
    def check_name_in_db(cls, value: str) -> str:

        stmt_select = select(Company).where(Company.name == value)

        with Session(engine) as session:
            answer_from_db = session.scalar(stmt_select)

        if answer_from_db is None:
            raise HTTPException(status_code=404,
                                detail="Такой компании не существует")
        
        return value
    

class CompanyAnswer(CompanyBase):
    "Модель ответа API после прочтения ответа из бд"

    id: int
    owner_id: int

    class Config:
        orm_mode = True


################################# Employee #################################


class EmployeeBase(BaseModel):
    "Базовый модель сотрудника"
    name: str


class EmployeeMany(BaseModel):
    "Модель для множественного добавления сотрудников в бд"
    
    array: List[EmployeeBase]


if __name__ == "__main__":
    pass
