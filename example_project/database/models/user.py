from datetime import datetime

from sqlalchemy import BigInteger, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime

from example_project.database.enums import (
    GradeEnum,
    RegisterStatus,
    StudentInstitution,
    StudentYear,
    UserRelative,
    UserResidence,
)
from .layer_base import Base


# ==============______USER______=========================================================================================== USER
class User(Base):
    __tablename__ = 'users'

    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(255))

    tg_phone: Mapped[str | None] = mapped_column(String(15))
    tg_id: Mapped[int | None] = mapped_column(BigInteger(), unique=True, nullable=True)
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=True)

    photo_passport: Mapped[str | None] = mapped_column(Text)
    photo_passback: Mapped[str | None] = mapped_column(Text)
    passport_series: Mapped[str | None] = mapped_column(String(10))

    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    referrer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)

    referrer: Mapped["User"] = relationship(
        "User",
        remote_side="User.id",  # ✅ Correct way to reference the parent
        back_populates="referrals", 
        lazy="selectin")

    referrals: Mapped[list["User"]] = relationship(
        "User",
        back_populates="referrer",
        cascade="all", 
        lazy="selectin")
    register_status: Mapped[RegisterStatus] = mapped_column(Enum(RegisterStatus), nullable=True)

    phones: Mapped[list["UserPhone"]] = relationship("UserPhone", back_populates='user', lazy="selectin")
    user_meta: Mapped["UserMeta"] = relationship("UserMeta", back_populates="user", uselist=False, lazy="selectin")
    sponsorship: Mapped["Sponsor"] = relationship("Sponsor", back_populates="user", uselist=False, lazy="selectin")

    grants: Mapped[list['GrantUsage']] = relationship("GrantUsage", back_populates='user', lazy="selectin")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user", lazy="selectin")
    messages: Mapped[list["InboxMessage"]] = relationship("InboxMessage", back_populates="user", lazy="selectin")
    penalties: Mapped[list["Penalty"]] = relationship("Penalty", back_populates="user", lazy="selectin")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="user", lazy="selectin")
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", primaryjoin="and_(foreign(Transaction.rel_id)==User.id)", viewonly=False, overlaps="transactions", lazy="selectin")

    promos: Mapped[list["PromoUsage"]] = relationship("PromoUsage", back_populates="user", lazy="selectin")
    grades: Mapped[list["Grade"]] = relationship("Grade", back_populates='user', lazy="selectin")

    __list_view_fields__ = ['id', 'first_name', 'phone']
    def short_repr(self):
        return f"{self.id} - {self.first_name} {self.last_name}"
    





# ==============______PHONE______=========================================================================================== PHONE
class UserPhone(Base):
    __tablename__ = 'user_phones'
    phone: Mapped[str | None] = mapped_column(String(15))
    relative: Mapped[UserRelative] = mapped_column(Enum(UserRelative), nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates='phones', lazy="selectin")
    
    __list_view_fields__ = ['id', 'phone', 'user.first_name', 'relative.name']
    def short_repr(self):
        return f"{self.id} - {self.phone} ({self.relative.value})"



# ==============______USER META______=========================================================================================== USER META
class UserMeta(Base):
    __tablename__ = 'user_metas'

    residence: Mapped[UserResidence | None] = mapped_column(Enum(UserResidence))
    works_at: Mapped[str | None] = mapped_column(String(255))
    treating: Mapped[str | None] = mapped_column(String(255))

    is_student: Mapped[bool] = mapped_column(default=False)
    student_year: Mapped[StudentYear | None] = mapped_column(Enum(StudentYear))
    student_institution: Mapped[StudentInstitution | None] = mapped_column(Enum(StudentInstitution))
    institute: Mapped[str | None] = mapped_column(String(255))

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), unique=True, nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="user_meta", lazy="selectin")

    document_medias: Mapped[list['Media']] = relationship('Media', primaryjoin="and_(foreign(Media.rel_id)==UserMeta.id)", viewonly=False, overlaps="afterfix_medias,beforefix_medias,start_medias,finish_medias,document_medias,medias", lazy="selectin")

    __list_view_fields__ = ['user.id', 'user.first_name', 'residence', 'treating[:50]']
    def short_repr(self):
        return f"{self.user.id} - {self.user.first_name} meta"
    



# ==============______GRADE______=========================================================================================== GRADE
class Grade(Base):
    __tablename__ = 'grades'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="grades", lazy="selectin")

    grade: Mapped[GradeEnum] = mapped_column(Enum(GradeEnum), default=GradeEnum.G_10, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)

    __list_view_fields__ = ['id', 'grade', 'comment[:50]', 'user.fist_name']
    def short_repr(self):
        return f"{self.id} - {self.grade.value}"