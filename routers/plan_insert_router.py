from typing import Annotated

from fastapi import APIRouter, UploadFile
from fastapi.params import Depends
from starlette import status
from starlette.responses import JSONResponse

from core.deps import get_plan_insert_service

from services.plan_insert_service import PlanService

load_data_rout = APIRouter(
    tags=["Plan"],
)


@load_data_rout.post(
    "/plans_insert",
    status_code=status.HTTP_200_OK,
    summary="Upload file with plan data",
    description="""
Uploads an Excel file with plans for a new month <br>
The file must contain the following columns:
- `Mісяць плану`: date with the first day of the target month (e.g., 2025-09-01)
- `Назва категорії плану` : (e.g. видача/збір)
- `Сума`: a non-empty numeric value (zero is allowed, but empty/negatives are not)
""",
)
async def plans_insert(
    plan_service: Annotated[PlanService, Depends(get_plan_insert_service)],
    file: UploadFile,
):

    return await plan_service.load_file(file.file)
