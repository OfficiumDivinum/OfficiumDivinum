from fastapi import APIRouter, HTTPException

router = APIRouter()

tasks = []


@router.get("/{task}")
def in_progress(task: str):
    """Query if the task is in progress."""
    if task in tasks:
        return {task: "In progress"}
    else:
        raise HTTPException(
            status_code=404,
            detail="No such task in progress.  Perhaps it has already finished?",
        )
