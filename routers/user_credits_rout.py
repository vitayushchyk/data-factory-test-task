from typing import Annotated

from fastapi import APIRouter, Depends


from core.deps import get_user_credits_service

from services.user_credits_service import UserCreditService

user_credits = APIRouter(tags=["User credits"], prefix="/user_credits")


@user_credits.get(
    "/{user_id}",
    description="Get all user credits",
)
async def get_user_credits(
    user_id: int,
    user_credits_service: Annotated[
        UserCreditService, Depends(get_user_credits_service)
    ],
):
    return await user_credits_service.get_all_user_credits(user_id)
