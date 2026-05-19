from sqlalchemy.orm import Session
from app.models import Game
from app.schemas import GameCreate


def create_game(db: Session, data: GameCreate) -> Game:
    game = Game(**data.model_dump())
    db.add(game)
    db.commit()
    db.refresh(game)
    return game


def get_game(db: Session, game_id: str) -> Game | None:
    return db.query(Game).filter(Game.id == game_id).first()


def list_games(db: Session, limit: int = 20, offset: int = 0) -> tuple[list[Game], int]:
    total = db.query(Game).count()
    items = db.query(Game).offset(offset).limit(limit).all()
    return items, total


def search_games(db: Session, q: str, limit: int = 20, offset: int = 0) -> tuple[list[Game], int]:
    query = db.query(Game).filter(Game.title.ilike(f"%{q}%"))
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    return items, total