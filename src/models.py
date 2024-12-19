from typing import List

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, BigInteger
from src.utils.db import Base, session


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    role: Mapped[str] = mapped_column(nullable=False)
    chat: Mapped[str] = mapped_column(nullable=False)

    sent_messages: Mapped[List["Messages"]] = relationship(
        "Messages", back_populates="from_user", foreign_keys="Messages.from_user_id"
    )
    received_messages: Mapped[List["Messages"]] = relationship(
        "Messages", back_populates="to_user", foreign_keys="Messages.to_user_id"
    )

    def __repr__(self):
        return f"User({self.role})"

    @staticmethod
    def get_user_by_tg_id(tg_id):
        return session.query(Users).filter_by(tg_id=tg_id).first()


class Messages(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(nullable=False)

    from_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    from_user: Mapped["Users"] = relationship(
        "Users", back_populates="sent_messages", foreign_keys=[from_user_id]
    )
    to_user: Mapped["Users"] = relationship(
        "Users", back_populates="received_messages", foreign_keys=[to_user_id]
    )

    def __repr__(self):
        return f"Message(from={self.from_user.role}, to={self.to_user.role})"
