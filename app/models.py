import enum
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Numeric,
    Boolean,
    ForeignKey,
    DateTime,
    Enum as SQLEnum,
    Time
)
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.database import Base


# --- ENUMS ---
class RoleEnum(str, enum.Enum):
    INDEPENDENT_BARBER = "INDEPENDENT_BARBER"
    SHOP_OWNER = "SHOP_OWNER"
    ADMIN = "ADMIN"


class SubscriptionStatusEnum(str, enum.Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    CANCELED = "CANCELED"


class VerificationStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class DayOfWeekEnum(str, enum.Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


# --- 1. USUARIOS Y AUTENTICACIÓN ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(RoleEnum), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    barber_profile = relationship("Barber", back_populates="user", uselist=False)
    barbershop = relationship("Barbershop", back_populates="owner", uselist=False)


# --- 2. BARBERÍA ---
class Barbershop(Base):
    __tablename__ = "barbershops"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    name = Column(String(150), nullable=False)
    bio = Column(Text, nullable=True)
    years_in_service = Column(Integer, default=0)
    phone = Column(String(20), nullable=False)
    avatar_url = Column(String(500), nullable=True)

    location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False, index=True)
    address_text = Column(String(255), nullable=True)

    subscription_status = Column(SQLEnum(SubscriptionStatusEnum), default=SubscriptionStatusEnum.SUSPENDED, index=True)
    allowed_barbers_count = Column(Integer, default=3, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="barbershop")
    barbers = relationship("Barber", back_populates="barbershop")
    images = relationship("BarbershopImage", back_populates="barbershop", cascade="all, delete-orphan")
    schedules = relationship("BarbershopSchedule", back_populates="barbershop", cascade="all, delete-orphan")
    services = relationship("ServiceCatalog", back_populates="barbershop", cascade="all, delete-orphan")
    packages = relationship("PackageCatalog", back_populates="barbershop", cascade="all, delete-orphan")


class BarbershopImage(Base):
    __tablename__ = "barbershop_images"

    id = Column(Integer, primary_key=True, index=True)
    barbershop_id = Column(Integer, ForeignKey("barbershops.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(String(500), nullable=False)
    display_order = Column(Integer, default=0)

    barbershop = relationship("Barbershop", back_populates="images")


class BarbershopSchedule(Base):
    __tablename__ = "barbershop_schedules"

    id = Column(Integer, primary_key=True, index=True)
    barbershop_id = Column(Integer, ForeignKey("barbershops.id", ondelete="CASCADE"), nullable=False)
    day_of_week = Column(SQLEnum(DayOfWeekEnum), nullable=False)
    is_closed = Column(Boolean, default=False)
    open_time = Column(Time, nullable=True)
    close_time = Column(Time, nullable=True)

    barbershop = relationship("Barbershop", back_populates="schedules")


# --- 3. BARBERO ---
class Barber(Base):
    __tablename__ = "barbers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    barbershop_id = Column(Integer, ForeignKey("barbershops.id", ondelete="SET NULL"), nullable=True)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    stage_name = Column(String(100), nullable=False, index=True)
    age = Column(Integer, nullable=False)
    phone = Column(String(20), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)

    location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True, index=True)
    approved_medals_count = Column(Integer, default=0, nullable=False)
    subscription_status = Column(SQLEnum(SubscriptionStatusEnum), default=SubscriptionStatusEnum.SUSPENDED, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="barber_profile")
    barbershop = relationship("Barbershop", back_populates="barbers")
    portfolio_images = relationship("BarberPortfolioImage", back_populates="barber", cascade="all, delete-orphan")
    awards = relationship("BarberAward", back_populates="barber", cascade="all, delete-orphan")
    services = relationship("ServiceCatalog", back_populates="barber", cascade="all, delete-orphan")
    packages = relationship("PackageCatalog", back_populates="barber", cascade="all, delete-orphan")


class BarberPortfolioImage(Base):
    __tablename__ = "barber_portfolio_images"

    id = Column(Integer, primary_key=True, index=True)
    barber_id = Column(Integer, ForeignKey("barbers.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(String(500), nullable=False)
    display_order = Column(Integer, default=0)

    barber = relationship("Barber", back_populates="portfolio_images")


class BarberAward(Base):
    __tablename__ = "barber_awards"

    id = Column(Integer, primary_key=True, index=True)
    barber_id = Column(Integer, ForeignKey("barbers.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False)
    proof_document_url = Column(String(500), nullable=False)
    status = Column(SQLEnum(VerificationStatusEnum), default=VerificationStatusEnum.PENDING, index=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)

    barber = relationship("Barber", back_populates="awards")


# --- 4. SERVICIOS Y COMBOS ---
class ServiceCatalog(Base):
    __tablename__ = "service_catalog"

    id = Column(Integer, primary_key=True, index=True)
    barber_id = Column(Integer, ForeignKey("barbers.id", ondelete="CASCADE"), nullable=True)
    barbershop_id = Column(Integer, ForeignKey("barbershops.id", ondelete="CASCADE"), nullable=True)

    service_name = Column(String(80), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    is_base_cut = Column(Boolean, default=False, index=True)

    barber = relationship("Barber", back_populates="services")
    barbershop = relationship("Barbershop", back_populates="services")


class PackageCatalog(Base):
    __tablename__ = "package_catalog"

    id = Column(Integer, primary_key=True, index=True)
    barber_id = Column(Integer, ForeignKey("barbers.id", ondelete="CASCADE"), nullable=True)
    barbershop_id = Column(Integer, ForeignKey("barbershops.id", ondelete="CASCADE"), nullable=True)

    title = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)

    barber = relationship("Barber", back_populates="packages")
    barbershop = relationship("Barbershop", back_populates="packages")