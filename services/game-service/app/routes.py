from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.infrastructure.cache import get_game_summary
from app.security import require_admin
from app import service, schemas

router = APIRouter(prefix="/v1/games", tags=["games"])


@router.post("/", response_model=schemas.GameOut, status_code=status.HTTP_201_CREATED)
def create_game(data: schemas.GameCreate, db: Session = Depends(get_db)):
    return service.add_game(db, data)


@router.get("/", response_model=schemas.GameList)
def list_games(limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    return service.fetch_all_games(db, limit, offset)


@router.get("/search", response_model=schemas.GameList)
def search_games(q: str, limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    return service.find_games(db, q, limit, offset)


@router.get("/{game_id}", response_model=schemas.GameOut)
def get_game(game_id: str, db: Session = Depends(get_db)):
    try:
        return service.fetch_game(db, game_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{game_id}/summary")
def get_game_summary_route(game_id: str):
    data = get_game_summary(game_id)
    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    return data


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_game(game_id: str, db: Session = Depends(get_db)):
    try:
        service.remove_game(db, game_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
