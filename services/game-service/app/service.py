from sqlalchemy.orm import Session
from app import repository
from app.schemas import GameCreate, GameOut, GameList


def add_game(db: Session, data: GameCreate) -> GameOut:
    game = repository.create_game(db, data)
    return GameOut.model_validate(game)


def fetch_game(db: Session, game_id: str) -> GameOut:
    game = repository.get_game(db, game_id)
    if game is None:
        raise ValueError(f"Game {game_id} not found")
    return GameOut.model_validate(game)


def fetch_all_games(db: Session, limit: int = 20, offset: int = 0) -> GameList:
    items, total = repository.list_games(db, limit, offset)
    return GameList(
        items=[GameOut.model_validate(g) for g in items],
        total=total,
        limit=limit,
        offset=offset,
    )


def find_games(db: Session, q: str, limit: int = 20, offset: int = 0) -> GameList:
    items, total = repository.search_games(db, q, limit, offset)
    return GameList(
        items=[GameOut.model_validate(g) for g in items],
        total=total,
        limit=limit,
        offset=offset,
    )
