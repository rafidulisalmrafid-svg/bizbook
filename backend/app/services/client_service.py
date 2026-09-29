from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.business import Client, ClientContact
from app.schemas.client import ClientCreate, ClientUpdate, ClientContactCreate

class ClientService:
    @staticmethod
    async def list_clients(db: AsyncSession, company_id: str, include_archived: bool = False) -> List[Client]:
        query = (
            select(Client)
            .where(Client.company_id == company_id)
            .options(selectinload(Client.contacts))
        )
        if not include_archived:
            query = query.where(Client.is_archived == False)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_client(db: AsyncSession, company_id: str, client_id: str) -> Client:
        result = await db.execute(
            select(Client)
            .where(Client.id == client_id, Client.company_id == company_id)
            .options(selectinload(Client.contacts))
        )
        client = result.scalar_one_or_none()
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
        return client

    @staticmethod
    async def create_client(db: AsyncSession, company_id: str, data: ClientCreate) -> Client:
        client = Client(company_id=company_id, **data.model_dump())
        db.add(client)
        await db.commit()
        await db.refresh(client)
        return await ClientService.get_client(db, company_id, client.id)

    @staticmethod
    async def update_client(db: AsyncSession, company_id: str, client_id: str, data: ClientUpdate) -> Client:
        client = await ClientService.get_client(db, company_id, client_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(client, key, value)
        await db.commit()
        await db.refresh(client)
        return client

    @staticmethod
    async def archive_client(db: AsyncSession, company_id: str, client_id: str) -> Client:
        client = await ClientService.get_client(db, company_id, client_id)
        client.is_archived = True
        await db.commit()
        await db.refresh(client)
        return client

    @staticmethod
    async def add_contact(db: AsyncSession, company_id: str, client_id: str, data: ClientContactCreate) -> ClientContact:
        await ClientService.get_client(db, company_id, client_id)
        contact = ClientContact(client_id=client_id, **data.model_dump())
        db.add(contact)
        await db.commit()
        await db.refresh(contact)
        return contact
