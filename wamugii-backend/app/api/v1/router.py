from fastapi import APIRouter

from app.api.v1 import (
    admin,
    auth,
    client,
    client_learning,
    courses,
    exams,
    domains,
    health,
    hosting,
    invoices,
    notifications,
    projects,
    project_files,
    project_members,
    project_milestones,
    quote_requests,
    services,
    settings,
    sitemap,
    support,
    team,
    users,
)

api_router = APIRouter()
# First, so an uptime monitor's path is never shadowed by a later router.
api_router.include_router(health.router)
api_router.include_router(sitemap.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(services.router)
api_router.include_router(admin.router)
api_router.include_router(projects.router)
api_router.include_router(project_milestones.router)
api_router.include_router(project_files.router)
api_router.include_router(project_members.router)
api_router.include_router(client.router)
api_router.include_router(courses.router)
api_router.include_router(client_learning.router)
api_router.include_router(exams.router)
api_router.include_router(quote_requests.router)
api_router.include_router(invoices.router)
api_router.include_router(notifications.router)
api_router.include_router(settings.router)
api_router.include_router(hosting.router)
api_router.include_router(support.router)
api_router.include_router(domains.router)
api_router.include_router(team.router)
