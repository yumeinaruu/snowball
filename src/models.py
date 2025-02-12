from typing import List

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, BigInteger
from src.utils.db import Base, session


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(nullable=False)
    course: Mapped[str] = mapped_column(nullable=False)

    sent_messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="from_user", foreign_keys="Message.from_user_id"
    )
    received_messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="to_user", foreign_keys="Message.to_user_id"
    )

    def __repr__(self):
        return f"User({self.name})"

    @staticmethod
    def is_exists(tg_id):
        return session.query(User).filter_by(tg_id=tg_id).count() > 0

    @staticmethod
    def get_by_tg_id(tg_id):
        return session.query(User).filter_by(tg_id=tg_id).first()

    @staticmethod
    def get_by_course(course):
        return session.query(User).filter_by(course=course).all()


class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(nullable=False)

    from_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    from_user: Mapped["User"] = relationship(
        "User", back_populates="sent_messages", foreign_keys=[from_user_id]
    )
    to_user: Mapped["User"] = relationship(
        "User", back_populates="received_messages", foreign_keys=[to_user_id]
    )

    def __repr__(self):
        return f"Message({id}, from={self.from_user.name}, to={self.to_user.name})"

    @staticmethod
    def get_count_messages_from_user(user_id):
        return Message.get_messages_from_user(user_id).count()

    @staticmethod
    def get_count_messages_to_user(user_id):
        return Message.get_messages_to_user(user_id).count()

    @staticmethod
    def get_messages_from_user(user_id):
        return session.query(Message).filter_by(from_user_id=user_id)

    @staticmethod
    def get_messages_to_user(user_id):
        return session.query(Message).filter_by(to_user_id=user_id)
