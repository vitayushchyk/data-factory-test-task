from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.connection import get_async_session
from schemas.credits_info_schema import UserCreditsRes
from services.user_credits_service import UserCreditCRUD

user_credits = APIRouter(tags=["User credits"], prefix="/user_credits")


@user_credits.get(
    "/{user_id}",
    description="Get all user credits",
)
async def get_user_credits(
    user_id: int, session: AsyncSession = Depends(get_async_session)
):
    crud = UserCreditCRUD(session)
    result = await crud.get_all_user_credits(user_id)

    return result
