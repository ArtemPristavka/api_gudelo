from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship
    )
from sqlalchemy import ForeignKey, create_engine
from typing import List


__all__ = ["Base", "engine", "Owner", "Employee", "Company"]

engine = create_engine("sqlite+pysqlite:///data_base_biznes.db")


class Base(DeclarativeBase):
    pass


class Owner(Base):
    "Таблица Owners (Владелец)"

    __tablename__ = "Owners"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]

    company: Mapped["Company"] = relationship(back_populates="owner",
                                              single_parent=True,
                                              lazy="selectin")
    
    def __repr__(self) -> str:
        answer = f"id: {self.id} " \
                f"name: {self.name} " \
                f"password: {self.password}"
        
        return answer
    

class Company(Base):
    "Таблица Companys (Компании)"
    
    __tablename__ = "Companys"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    owner_id: Mapped[int] = mapped_column(ForeignKey("Owners.id",
                                                     onupdate="CASCADE"))

    owner: Mapped["Owner"] = relationship(back_populates="company",
                                          single_parent=True,
                                          lazy="select")
    
    employee: Mapped[List["Employee"]] = relationship(back_populates="company",
                                                      lazy="selectin",
                                                      cascade="all")
    
    def __repr__(self) -> str:
        answer = f"id: {self.id} " \
                f"name: {self.name} " \
                f"owner_id: {self.owner_id}"
        
        return answer


class Employee(Base):
    "Таблица Employees (Сотрудники) "
    
    __tablename__ = "Employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    password: Mapped[str]
    company_id: Mapped[int] = mapped_column(ForeignKey("Companys.id",
                                                       onupdate="CASCADE",
                                                        ondelete="CASCADE" ))

    company: Mapped["Company"] = relationship(back_populates="employee",
                                              single_parent=True,
                                              lazy="select")

    def __repr__(self) -> str:
        answer = f"id: {self.id} " \
                f"name: {self.name} " \
                f"password: {self.password} " \
                f"company_id: {self.company_id}"
        
        return answer


