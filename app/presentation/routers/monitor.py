"""
Monitor router - for debugging and monitoring API requests.
Part of Presentation layer.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel

from app.core.dependencies import get_db, get_current_user


router = APIRouter(prefix="/monitor", tags=["monitor"])


# In-memory transaction store (for simplicity - could be Redis or DB)
transactions_store: List[dict] = []
MAX_TRANSACTIONS = 100


class Transaction(BaseModel):
    """Transaction model."""
    id: str
    timestamp: str
    method: str
    endpoint: str
    status: str
    statusCode: int | None = None
    duration: int | None = None
    error: str | None = None
    userId: str | None = None
    conversationId: str | None = None
    requestBody: dict | str | None = None
    responseBody: dict | str | None = None


@router.get("/transactions", response_model=List[Transaction])
async def get_transactions(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get recent API transactions.
    Returns last 100 transactions.
    """
    # Return transactions in reverse chronological order
    return list(reversed(transactions_store[-MAX_TRANSACTIONS:]))


@router.post("/retry/{transaction_id}")
async def retry_transaction(
    transaction_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retry a failed transaction.
    Note: This is a placeholder - actual retry logic depends on transaction type.
    """
    # Find transaction
    tx = next((t for t in transactions_store if t["id"] == transaction_id), None)

    if not tx:
        return {"success": False, "error": "Transaction not found"}

    # TODO: Implement actual retry logic based on endpoint
    # For now, just mark as retried
    tx["status"] = "pending"
    tx["error"] = None

    return {"success": True, "transaction": tx}


@router.post("/clear")
async def clear_transactions(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Clear all transaction history.
    """
    global transactions_store
    transactions_store = []
    return {"success": True, "message": "All transactions cleared"}


def log_transaction(
    method: str,
    endpoint: str,
    status: str,
    status_code: int | None = None,
    duration: int | None = None,
    error: str | None = None,
    user_id: str | None = None,
    conversation_id: str | None = None,
    request_body: dict | str | None = None,
    response_body: dict | str | None = None,
):
    """
    Log a transaction to the monitor.
    Called by middleware or endpoint handlers.
    """
    import uuid

    transaction = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "method": method,
        "endpoint": endpoint,
        "status": status,
        "statusCode": status_code,
        "duration": duration,
        "error": error,
        "userId": user_id,
        "conversationId": conversation_id,
        "requestBody": request_body,
        "responseBody": response_body,
    }

    transactions_store.append(transaction)

    # Keep only last MAX_TRANSACTIONS
    if len(transactions_store) > MAX_TRANSACTIONS:
        transactions_store.pop(0)
