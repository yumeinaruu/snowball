from typing import List

from sqlalchemy.orm import mapped_column, Mapped, relationship
from src.utils.db import Base, session


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(nullable=False)
    chat: Mapped[str] = mapped_column(nullable=False)
    messages: Mapped[List["Messages"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"User({self.role})"

    @staticmethod
    def get_user_by_tg_id(tg_id):
        return session.query(Users).filter_by(tg_id=tg_id).first()


class Messages(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[int] = mapped_column()
    to_user: Mapped["Users"] = relationship(back_populates="messages")
    from_user: Mapped["Users"] = relationship(back_populates="messages")

    def __repr__(self):
        return f"Message({self.from_user.role})"