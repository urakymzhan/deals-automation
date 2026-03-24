from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from datetime import datetime, timezone
from config import DATABASE_URL


engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class TrackedItem(Base):
    """An item the user wants to track."""
    __tablename__ = "tracked_items"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    source = Column(String, nullable=False)       # "ebay", "amazon", etc.
    target_price = Column(Float, nullable=True)   # alert if price drops below this
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    active = Column(Boolean, default=True)


class PriceHistory(Base):
    """A recorded price snapshot for a tracked item."""
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    title = Column(String, nullable=True)
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class HomeSearch(Base):
    """A zip code + criteria to monitor for home deals."""
    __tablename__ = "home_searches"

    id = Column(Integer, primary_key=True)
    label = Column(String, nullable=False)           # friendly name, e.g. "Chicago flips"
    zip_code = Column(String, nullable=False)
    max_price = Column(Float, nullable=True)         # alert on listings below this
    min_beds = Column(Integer, nullable=True)
    min_baths = Column(Float, nullable=True)
    max_days_on_market = Column(Integer, nullable=True)  # flag stale listings
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    active = Column(Boolean, default=True)


class PropertySnapshot(Base):
    """A recorded snapshot of a property listing."""
    __tablename__ = "property_snapshots"

    id = Column(Integer, primary_key=True)
    search_id = Column(Integer, nullable=False)
    zpid = Column(String, nullable=False)            # Zillow property ID
    address = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    beds = Column(Integer, nullable=True)
    baths = Column(Float, nullable=True)
    sqft = Column(Float, nullable=True)
    days_on_market = Column(Integer, nullable=True)
    url = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)        # primary listing photo
    arv_estimate = Column(Float, nullable=True)      # After Repair Value estimate
    estimated_profit = Column(Float, nullable=True)  # ARV - price - rehab
    price_drop = Column(Float, nullable=True)        # drop from previous snapshot (null if no drop)
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def init_db():
    Base.metadata.create_all(engine)
    # Add new columns to existing tables if they don't exist yet (safe to run repeatedly)
    import sqlalchemy
    new_cols = [
        ("photo_url", "TEXT"),
        ("arv_estimate", "FLOAT"),
        ("estimated_profit", "FLOAT"),
        ("price_drop", "FLOAT"),
    ]
    for col, col_type in new_cols:
        with engine.connect() as conn:
            try:
                conn.execute(sqlalchemy.text(
                    f"ALTER TABLE property_snapshots ADD COLUMN {col} {col_type}"
                ))
                conn.commit()
                print(f"[DB] Added column: {col}")
            except Exception:
                pass  # column already exists
