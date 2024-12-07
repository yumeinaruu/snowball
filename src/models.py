from sqlalchemy.orm import mapped_column, Mapped, relationship
from src.utils.db import Base


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    messages: Mapped["Messages"] = relationship(back_populates="user")


class Messages(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[int] = mapped_column()
    to_user_id: Mapped["Users"] = relationship()
    user_id: Mapped["Users"] = relationship()
