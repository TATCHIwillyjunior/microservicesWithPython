from sqlalchemy.orm import Session
from app import repository
from app.infrastructure.cache import delete_game_summary, set_game_summary
from app.schemas import GameCreate, GameOut, GameList


def add_game(db: Session, data: GameCreate) -> GameOut:
    game = repository.create_game(db, data)
    set_game_summary(game.id, {
        "id": game.id,
        "title": game.title,
        "genre": game.genre,
        "platform": game.platform,
    })
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


def remove_game(db: Session, game_id: str) -> None:
    deleted = repository.delete_game(db, game_id)
    if not deleted:
        raise ValueError(f"Game {game_id} not found")
    delete_game_summary(game_id)
