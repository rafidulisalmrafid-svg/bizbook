from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.business import Service
from app.schemas.service import ServiceCreate, ServiceUpdate

class ServiceCatalogService:
    @staticmethod
    async def list_services(db: AsyncSession, company_id: str, include_archived: bool = False) -> List[Service]:
        query = select(Service).where(Service.company_id == company_id)
        if not include_archived:
            query = query.where(Service.is_archived == False)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_service(db: AsyncSession, company_id: str, service_id: str) -> Service:
        result = await db.execute(
            select(Service).where(Service.id == service_id, Service.company_id == company_id)
        )
        service = result.scalar_one_or_none()
        if not service:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
        return service

    @staticmethod
    async def create_service(db: AsyncSession, company_id: str, data: ServiceCreate) -> Service:
        service = Service(company_id=company_id, **data.model_dump())
        db.add(service)
        await db.commit()
        await db.refresh(service)
        return service

    @staticmethod
    async def update_service(db: AsyncSession, company_id: str, service_id: str, data: ServiceUpdate) -> Service:
        service = await ServiceCatalogService.get_service(db, company_id, service_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(service, key, value)
        await db.commit()
        await db.refresh(service)
        return service

    @staticmethod
    async def archive_service(db: AsyncSession, company_id: str, service_id: str) -> Service:
        service = await ServiceCatalogService.get_service(db, company_id, service_id)
        service.is_archived = True
        service.is_active = False
        await db.commit()
        await db.refresh(service)
        return service
