import logging
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException, Request, Depends
from repositories.postgres_repository import PostgresDB
from services.entry_service import EntryService
from models.entry import Entry, EntryCreate


router = APIRouter()
logger = logging.getLogger("journal")

# Dependency: give each request a fresh service with a fresh DB connection
async def get_entry_service() -> AsyncGenerator[EntryService, None]:
    async with PostgresDB() as db:
        yield EntryService(db)


# -----------------------------
# CREATE ENTRY
# -----------------------------
@router.post("/entries")
async def create_entry(entry_data: EntryCreate, entry_service: EntryService = Depends(get_entry_service)):
    """Create a new journal entry."""
    try:
        entry = Entry(
            work=entry_data.work,
            struggle=entry_data.struggle,
            intention=entry_data.intention
        )

        created_entry = await entry_service.create_entry(entry.model_dump())

        return {
            "detail": "Entry created successfully",
            "entry": created_entry
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating entry: {str(e)}")


# -----------------------------
# GET ALL ENTRIES
# -----------------------------
@router.get("/entries")
async def get_all_entries(entry_service: EntryService = Depends(get_entry_service)):
    """Retrieve all journal entries."""
    result = await entry_service.get_all_entries()
    return {"entries": result, "count": len(result)}


# -----------------------------
# GET ENTRY BY ID
# -----------------------------
@router.get("/entries/{entry_id}")
async def get_entry(entry_id: str, entry_service: EntryService = Depends(get_entry_service)):
    """Retrieve a specific journal entry by ID."""
    entry = await entry_service.get_entry(entry_id)

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    return {"entry": entry}


# -----------------------------
# UPDATE ENTRY
# -----------------------------
@router.patch("/entries/{entry_id}")
async def update_entry(entry_id: str, entry_update: dict, entry_service: EntryService = Depends(get_entry_service)):
    """Update an existing journal entry."""
    result = await entry_service.update_entry(entry_id, entry_update)

    if not result:
        raise HTTPException(status_code=404, detail="Entry not found")

    return {
        "detail": "Entry updated successfully",
        "entry": result
    }


# -----------------------------
# DELETE ENTRY BY ID
# -----------------------------
@router.delete("/entries/{entry_id}")
async def delete_entry(entry_id: str, entry_service: EntryService = Depends(get_entry_service)):
    """Delete a specific journal entry by ID."""
    entry = await entry_service.get_entry(entry_id)

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    await entry_service.delete_entry(entry_id)

    return {
        "detail": "Entry deleted successfully",
        "deleted_id": entry_id
    }


# -----------------------------
# DELETE ALL ENTRIES
# -----------------------------
@router.delete("/entries")
async def delete_all_entries(entry_service: EntryService = Depends(get_entry_service)):
    """Delete all journal entries."""
    await entry_service.delete_all_entries()
    return {"detail": "All entries deleted"}
