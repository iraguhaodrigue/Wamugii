from fastapi import APIRouter

from app.api.v1 import (
    admin,
    auth,
    client,
    invoices,
    notifications,
    projects,
    project_files,
    project_milestones,
    quote_requests,
    services,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(services.router)
api_router.include_router(admin.router)
api_router.include_router(projects.router)
api_router.include_router(project_milestones.router)
api_router.include_router(project_files.router)
api_router.include_router(client.router)
api_router.include_router(quote_requests.router)
api_router.include_router(invoices.router)
api_router.include_router(notifications.router)
