import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    Enum,
    Text,
    Float
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from app.database import Base


# --- ENUMS Y ALIAS DE COMPATIBILIDAD ---
class UserRole(str, enum.Enum):
    CLIENT = "client"
    BARBER = "barber"
    BARBERSHOP_OWNER = "barbershop_owner"
    ADMIN = "admin"

RoleEnum = UserRole


class VerificationStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    TRIALING = "trialing"

SubscriptionStatusEnum = SubscriptionStatus


# --- MODELOS ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.CLIENT, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    barber_profile = relationship("BarberProfile", back_populates="user", uselist=False)
    owned_barbershops = relationship("Barbershop", back_populates="owner")


class Barbershop(Base):
    __tablename__ = "barbershops"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(150), nullable=False, index=True)
    description = Column(Text, nullable=True)
    address = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # Redes sociales y sitio web (opcionales)
    instagram_url = Column(String(255), nullable=True)
    tiktok_url = Column(String(255), nullable=True)
    facebook_url = Column(String(255), nullable=True)
    website_url = Column(String(255), nullable=True)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)

    max_barbers = Column(Integer, default=3, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="owned_barbershops")
    barbers = relationship("BarberProfile", back_populates="barbershop")
    subscriptions = relationship("Subscription", back_populates="barbershop")


class BarberProfile(Base):
    __tablename__ = "barber_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    barbershop_id = Column(Integer, ForeignKey("barbershops.id"), nullable=True)
    bio = Column(Text, nullable=True)
    years_of_experience = Column(Integer, default=0, nullable=False)
    specialties = Column(String(255), nullable=True)

    # Redes sociales y sitio web (opcionales)
    instagram_url = Column(String(255), nullable=True)
    tiktok_url = Column(String(255), nullable=True)
    facebook_url = Column(String(255), nullable=True)
    website_url = Column(String(255), nullable=True)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)

    is_independent = Column(Boolean, default=True, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="barber_profile")
    barbershop = relationship("Barbershop", back_populates="barbers")
    awards = relationship("BarberAward", back_populates="barber")
    portfolio_images = relationship("BarberPortfolioImage", back_populates="barber")

# Alias de compatibilidad para routers antiguos
Barber = BarberProfile


class BarberAward(Base):
    __tablename__ = "barber_awards"

    id = Column(Integer, primary_key=True, index=True)
    barber_id = Column(Integer, ForeignKey("barber_profiles.id"), nullable=False)
    title = Column(String(150), nullable=False)
    organization = Column(String(150), nullable=False)
    year = Column(Integer, nullable=False)
    certificate_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    barber = relationship("BarberProfile", back_populates="awards")


class BarberPortfolioImage(Base):
    __tablename__ = "barber_portfolio_images"

    id = Column(Integer, primary_key=True, index=True)
    barber_id = Column(Integer, ForeignKey("barber_profiles.id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    barber = relationship("BarberProfile", back_populates="portfolio_images")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    barbershop_id = Column(Integer, ForeignKey("barbershops.id"), nullable=False)
    stripe_subscription_id = Column(String(100), unique=True, nullable=True)
    tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False)
    max_seats = Column(Integer, default=3, nullable=False)
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    barbershop = relationship("Barbershop", back_populates="subscriptions")