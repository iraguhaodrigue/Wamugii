from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import DbDep, OptionalUser, require_roles
from app.crud import service as service_crud
from app.models.user import Role, User
from app.schemas.service import ServiceCreate, ServiceRead, ServiceUpdate

router = APIRouter(prefix="/services", tags=["services"])


def _is_staff(user: User | None) -> bool:
    return user is not None and user.role in (Role.ADMIN, Role.STAFF)


@router.get("", response_model=list[ServiceRead])
def list_services(
    db: DbDep,
    current_user: OptionalUser,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: str | None = None,
    search: str | None = None,
    include_inactive: bool = False,
):
    include_inactive = include_inactive and _is_staff(current_user)
    return service_crud.list_services(
        db,
        limit=limit,
        offset=offset,
        category=category,
        search=search,
        include_inactive=include_inactive,
    )


@router.get("/{service_id}", response_model=ServiceRead)
def get_service(service_id: int, db: DbDep, current_user: OptionalUser):
    service = service_crud.get_by_id(db, service_id)
    if not service or (not service.is_active and not _is_staff(current_user)):
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.post(
    "",
    response_model=ServiceRead,
    status_code=201,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.STAFF))],
)
def create_service(data: ServiceCreate, db: DbDep):
    return service_crud.create(db, data)


@router.patch(
    "/{service_id}",
    response_model=ServiceRead,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.STAFF))],
)
def update_service(service_id: int, data: ServiceUpdate, db: DbDep):
    service = service_crud.get_by_id(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service_crud.update(db, service, data)


@router.delete(
    "/{service_id}",
    response_model=ServiceRead,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.STAFF))],
)
def delete_service(service_id: int, db: DbDep):
    service = service_crud.get_by_id(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service_crud.soft_delete(db, service)
