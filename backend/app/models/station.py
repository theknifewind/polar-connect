"""Station ORM model — polar research stations."""

from sqlalchemy import Column, JSON, String, Text

from app.database import Base


class Station(Base):
    __tablename__ = "stations"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    region = Column(String)                # "Schirmacher Oasis, Antarctica"
    description = Column(Text)
    established = Column(String)           # "1989"
    number = Column(String)                # "01"
    facts = Column(JSON, default=list)     # ["71°45′S · 11°44′E", …]
    color = Column(String, default="cyan") # Map marker color key
    map_x = Column(String)                 # CSS left % for map overlay
    map_y = Column(String)                 # CSS top % for map overlay
