from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.connection import get_async_session
from schemas.user_credits_schema import UserCreditsResponse
from services.user_serv import UserCreditCRUD

user_credits = APIRouter(tags=["User credits"])


@user_credits.get(
    "/user_credits/{user_id}",
    response_model=UserCreditsResponse,
    description="Get all user credits",
)
async def get_user_credits(
    user_id: int, session: AsyncSession = Depends(get_async_session)
):
    crud = UserCreditCRUD(session)
    return await crud.get_user_credits_full(user_id)
