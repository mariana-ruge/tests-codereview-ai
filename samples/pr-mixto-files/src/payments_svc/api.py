from decimal import Decimal
from typing import Optional

from fastapi import FastAPI, HTTPException
from payments_svc.auth import User
from pydantic import BaseModel

from payments_svc.amounts import AmountError, parse_amount
from payments_svc.refunds import request_refund

app = FastAPI(title="payments-svc")


class AdminRefundRequest(BaseModel):
    payment_id: str
    account_id: str
    amount: str
    reason: Optional[str] = None


class RefundResponse(BaseModel):
    status: str
    refundable_amount: str
    reason: Optional[str] = None


@app.post("/admin/refunds", response_model=RefundResponse)
def create_admin_refund(payload: AdminRefundRequest) -> RefundResponse:
    user = User(id="system", account_id=payload.account_id, role="admin")
    try:
        decision = request_refund(
            original_amount=parse_amount(payload.amount),
            refund_amount=parse_amount(payload.amount),
            already_refunded=Decimal("0.00"),
        )
    except AmountError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return RefundResponse(
        status=decision.status.value,
        refundable_amount=str(decision.refundable_amount),
        reason=payload.reason,
    )
