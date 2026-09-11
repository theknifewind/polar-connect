"""Seed runner — populates database on first boot.

Creates:
  - Default admin account (from ADMIN_EMAIL / ADMIN_PASSWORD)
  - 3 polar stations (Maitri, Bharati, Himadri)
  - 6 learning topics with 18 quiz questions
  - 4 media stories
  - 8 repository items (matching frontend polaris.ts seed data)
  - ChromaDB index for items with raw_text
"""

from __future__ import annotations

import json
import logging
import os
import uuid

from sqlalchemy.orm import Session

from app.config import settings
from app.core.auth import hash_password
from app.database import SessionLocal, init_db
from app.models.admin import AdminAccount
from app.models.learning import LearningTopic, QuizQuestion
from app.models.media import MediaStory
from app.models.repository import RepositoryItem
from app.models.station import Station

logger = logging.getLogger(__name__)
SEEDS_DIR = os.path.dirname(os.path.abspath(__file__))


def run_seeds() -> None:
    """Initialise DB tables and preload seed data (idempotent)."""
    init_db()
    db = SessionLocal()
    try:
        _seed_admin(db)
        _seed_stations(db)
        _seed_topics(db)
        _seed_media(db)
        _seed_repository(db)
        _index_pending(db)
        logger.info("✓ Seed data loaded successfully")
    except Exception:
        db.rollback()
        logger.exception("Seed runner failed")
        raise
    finally:
        db.close()


# ── Admin ────────────────────────────────────────────────────

def _seed_admin(db: Session) -> None:
    if db.query(AdminAccount).filter(AdminAccount.email == settings.ADMIN_EMAIL).first():
        logger.info("Admin already exists: %s", settings.ADMIN_EMAIL)
        return
    db.add(AdminAccount(
        id=str(uuid.uuid4()),
        email=settings.ADMIN_EMAIL,
        password_hash=hash_password(settings.ADMIN_PASSWORD),
    ))
    db.commit()
    logger.info("✓ Created admin: %s", settings.ADMIN_EMAIL)


# ── Stations ─────────────────────────────────────────────────

def _seed_stations(db: Session) -> None:
    if db.query(Station).count():
        return
    with open(os.path.join(SEEDS_DIR, "stations_seed.json"), encoding="utf-8") as f:
        data = json.load(f)
    for item in data:
        db.add(Station(**item))
    db.commit()
    logger.info("✓ Seeded %d stations", len(data))


# ── Learning topics + quizzes ────────────────────────────────

def _seed_topics(db: Session) -> None:
    if db.query(LearningTopic).count():
        return
    with open(os.path.join(SEEDS_DIR, "topics_seed.json"), encoding="utf-8") as f:
        data = json.load(f)
    for td in data["topics"]:
        questions = td.pop("questions", [])
        topic = LearningTopic(**td)
        db.add(topic)
        db.flush()
        for q in questions:
            q["topic_id"] = topic.id
            db.add(QuizQuestion(**q))
    db.commit()
    logger.info("✓ Seeded %d learning topics with quizzes", len(data["topics"]))


# ── Media stories ────────────────────────────────────────────

def _seed_media(db: Session) -> None:
    if db.query(MediaStory).count():
        return
    with open(os.path.join(SEEDS_DIR, "media_seed.json"), encoding="utf-8") as f:
        data = json.load(f)
    for item in data:
        db.add(MediaStory(**item))
    db.commit()
    logger.info("✓ Seeded %d media stories", len(data))


# ── Repository items ────────────────────────────────────────

def _seed_repository(db: Session) -> None:
    if db.query(RepositoryItem).count():
        return

    items = [
        dict(id="exp-43", type="Report",
             title="43rd Indian Antarctic Expedition",
             summary="A field report on atmospheric observations, glaciology and biological sampling conducted across the Maitri region.",
             year=2023, region="Antarctica",
             topics=["Expedition", "Climate change", "Glaciology"],
             meta="PDF · 86 pages",
             accent="from-cyan-300/30 via-sky-500/10 to-transparent", icon="▱",
             raw_text="The 43rd Indian Antarctic Expedition (2023) was a comprehensive scientific mission conducted in the Maitri region of Antarctica. The expedition brought together researchers from multiple disciplines including atmospheric science, glaciology, and biology. Key activities included monitoring atmospheric conditions, studying snow accumulation patterns, collecting biological samples, and maintaining long-term observation records. The team observed significant seasonal variations in ice dynamics and atmospheric composition. Snow accumulation measurements near Maitri Station revealed important data about surface energy balance and its relationship to broader climate patterns. Biological sampling focused on extremophilic organisms that thrive in Antarctica's harsh conditions, providing insights into adaptation mechanisms. The expedition also deployed new meteorological instruments to enhance the existing observation network. Data collected during this expedition contributes to India's growing polar research database and supports international collaborative efforts to understand Antarctic climate systems."),

        dict(id="ocean-24", type="Dataset",
             title="Southern Ocean Carbon Flux Observations",
             summary="Curated measurements from transects around the Indian Ocean sector of Antarctica.",
             year=2024, region="Southern Ocean",
             topics=["Oceanography", "Climate change"],
             meta="CSV · 14.2 MB",
             accent="from-emerald-300/25 via-teal-500/10 to-transparent", icon="⌁",
             raw_text="The Southern Ocean Carbon Flux dataset contains detailed measurements from ocean transects conducted in the Indian Ocean sector of Antarctica during 2024. These observations include dissolved CO₂ concentrations, pH levels, temperature profiles, and biological productivity indicators. The Southern Ocean plays a critical role in global carbon cycling, absorbing approximately 40% of anthropogenic CO₂ entering the oceans. This dataset captures seasonal variations in carbon uptake and release patterns, particularly during the transition from winter sea ice cover to open water conditions."),

        dict(id="maitri-paper", type="Publication",
             title="Snow accumulation dynamics near Maitri Station",
             summary="Peer-reviewed analysis of seasonal snow accumulation and its relationship to surface energy balance.",
             year=2022, region="Antarctica",
             topics=["Glaciology", "Maitri"],
             meta="Journal article · 12 min read",
             accent="from-indigo-300/30 via-violet-500/10 to-transparent", icon="✦",
             raw_text="This peer-reviewed study presents a comprehensive analysis of snow accumulation patterns in the vicinity of Maitri Station, Schirmacher Oasis, Antarctica. Using a combination of automatic weather station data, snow stake measurements, and ground-penetrating radar surveys, the research quantifies seasonal and inter-annual variability in snow accumulation over a five-year period (2017-2022). Results show that wind redistribution is the dominant factor controlling local snow accumulation, with katabatic winds creating significant spatial heterogeneity. The study also examines the surface energy balance components and their role in determining melt versus accumulation conditions."),

        dict(id="bharati-video", type="Video",
             title="Inside Bharati: India's polar laboratory",
             summary="A short visual field note from the newest of India's Antarctic research stations.",
             year=2024, region="Antarctica",
             topics=["Stations", "Education"],
             meta="Video · 04:18",
             accent="from-orange-300/25 via-amber-500/10 to-transparent", icon="▶"),

        dict(id="arctic-brief", type="News",
             title="New observations strengthen Arctic–monsoon links",
             summary="Researchers share early insights from India's Arctic research programme and its climate connections.",
             year=2024, region="Arctic",
             topics=["Climate change", "Arctic"],
             meta="News · 5 min read",
             accent="from-pink-300/25 via-fuchsia-500/10 to-transparent", icon="↗",
             raw_text="Recent observations from India's Himadri research station in Svalbard are revealing stronger-than-expected connections between Arctic climate dynamics and the Indian monsoon system. Research teams have identified correlations between Arctic sea ice extent and monsoon rainfall patterns, suggesting that changes in the Arctic could have direct implications for India's agricultural seasons and water resources."),

        dict(id="polar-101", type="Learning",
             title="Polar Science 101",
             summary="A beginner-friendly introduction to ice, oceans, climate systems and the scientists who study them.",
             year=2024, region="Antarctica",
             topics=["Education", "Basics"],
             meta="Lesson · 8 min",
             accent="from-yellow-200/30 via-cyan-500/10 to-transparent", icon="◎"),

        dict(id="photo-ice", type="Photo",
             title="Field notes: blue ice and long shadows",
             summary="A photo essay from the summer traverse documenting wind-carved ice formations.",
             year=2021, region="Antarctica",
             topics=["Photography", "Fieldwork"],
             meta="Gallery · 18 images",
             accent="from-sky-300/30 via-blue-600/10 to-transparent", icon="▧"),

        dict(id="tech-station", type="Publication",
             title="Designing for the cold: polar technology",
             summary="How instruments, shelters and field protocols are adapted for reliable work in extreme environments.",
             year=2020, region="Antarctica",
             topics=["Technology", "Stations"],
             meta="Explainer · 10 min read",
             accent="from-teal-300/25 via-slate-500/10 to-transparent", icon="⌘",
             raw_text="Operating in polar environments requires fundamental adaptations to standard scientific instruments, shelter designs, and operational protocols. This explainer reviews the engineering challenges of polar research: extreme cold (below -40°C), high winds (up to 300 km/h katabatic gusts), limited daylight, and remote logistics. Key topics include thermal management for electronics, wind-resistant station architecture, renewable energy systems in polar settings, and field safety protocols. India's Bharati Station represents modern polar engineering with its aerodynamic container-based design."),
    ]

    for item_data in items:
        db.add(RepositoryItem(**item_data, index_status="pending"))
    db.commit()
    logger.info("✓ Seeded %d repository items", len(items))


# ── ChromaDB indexing of seeded items ────────────────────────

def _index_pending(db: Session) -> None:
    """Index all repository items that have raw_text but are still pending."""
    pending = (
        db.query(RepositoryItem)
        .filter(
            RepositoryItem.index_status == "pending",
            RepositoryItem.raw_text.isnot(None),
            RepositoryItem.raw_text != "",
        )
        .all()
    )
    if not pending:
        return

    from app.services.ingestion import ingest_document

    for item in pending:
        try:
            result = ingest_document(
                doc_id=item.id,
                raw_text=item.raw_text,
                doc_type=item.type or "",
                region=item.region or "",
                year=item.year or 0,
            )
            item.index_status = result
        except Exception as exc:
            logger.warning("Failed to index %s: %s", item.id, exc)
            item.index_status = "failed"

    db.commit()
    logger.info("✓ Indexed %d repository items into ChromaDB", len(pending))
