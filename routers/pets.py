from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from dependencies import get_current_user_id
from database.db import pool
from database import pets as petsdb
from database import friends as friendsdb

router = APIRouter(tags=["pets"])


@router.post("/create_pet")
def create_pets(user_id: Annotated[int, Depends(get_current_user_id)], father_id, name):
    with pool.connection() as conn, conn.cursor() as cursor:
        coupleId = friendsdb.get_couple_id(cursor, user_id, father_id)
        if coupleId is None:
            raise HTTPException(status_code=404, detail="Can't create pet without being friends")

        petid = petsdb.create_pet(cursor, coupleId, name)
        if petid is None:
            raise HTTPException(status_code=409, detail="Pet exists")

    return {"success": True, "petId": petid}


@router.get("/get_pet")
def get_pet(user_id: Annotated[int, Depends(get_current_user_id)], fatherId: int):
    with pool.connection() as conn, conn.cursor() as cursor:
        coupleId = friendsdb.get_couple_id(cursor, user_id, fatherId)
        if coupleId is None:
            raise HTTPException(status_code=404, detail="Can't get pet without being friends")

        petId = petsdb.get_pet(cursor, coupleId)
    if petId is None:
        raise HTTPException(status_code=404, detail="No pet found")

    return {"success": True, "petId": petId}



