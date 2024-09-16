import uuid
from datetime import datetime
from sqlalchemy import Uuid, ForeignKey, TIMESTAMP, text, BigInteger
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    repr_cols_num = 3
    repr_cols: tuple[str, ...] = ("email", "id", "first_name", "last_name")

    created_at: Mapped[datetime] = mapped_column(
        type_=TIMESTAMP(timezone=True),
        server_default=text("TIMEZONE('utc', now())"),
    )
    update_at: Mapped[datetime] = mapped_column(
        type_=TIMESTAMP(timezone=True),
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=text("TIMEZONE('utc', now())"),
        nullable=True
    )
    
    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"
    

class User(Base):
    __tablename__ = "user_account"
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(unique=True, index=True)
    first_name: Mapped[str]
    hashed_password: Mapped[str] = mapped_column()