from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import async_session, User, Subscription


async def get_or_create_user(chat_id: int) -> User:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.chat_id == chat_id))
        user = result.scalar_one_or_none()
        if not user:
            user = User(chat_id=chat_id)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user


async def subscribe(chat_id: int, query: str) -> bool:
    async with async_session() as session:
        user = await get_or_create_user(chat_id)
        exists = await session.execute(
            select(Subscription).where(
                Subscription.user_id == user.id,
                Subscription.query == query,
            )
        )
        if exists.scalar_one_or_none():
            return False

        session.add(Subscription(user_id=user.id, query=query))
        await session.commit()
        return True


async def unsubscribe(chat_id: int, query: str) -> bool:
    async with async_session() as session:
        user = await get_or_create_user(chat_id)
        result = await session.execute(
            delete(Subscription)
            .where(Subscription.user_id == user.id, Subscription.query == query)
            .returning(Subscription.id)
        )
        await session.commit()
        return result.scalar_one_or_none() is not None


async def get_subscriptions(chat_id: int) -> list[str]:
    async with async_session() as session:
        user = await get_or_create_user(chat_id)
        result = await session.execute(
            select(Subscription.query).where(Subscription.user_id == user.id)
        )
        return list(result.scalars().all())


async def is_subscribed(chat_id: int, query: str) -> bool:
    async with async_session() as session:
        user = await get_or_create_user(chat_id)
        result = await session.execute(
            select(Subscription).where(
                Subscription.user_id == user.id,
                Subscription.query == query,
            )
        )
        return result.scalar_one_or_none() is not None


async def get_all_subscriptions() -> list[tuple[int, str]]:
    async with async_session() as session:
        result = await session.execute(
            select(User.chat_id, Subscription.query)
            .join(Subscription, Subscription.user_id == User.id)
        )
        return result.all()
