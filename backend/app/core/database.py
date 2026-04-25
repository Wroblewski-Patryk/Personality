from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine


class Database:
    def __init__(self, database_url: str):
        self.engine: AsyncEngine = create_async_engine(database_url, pool_pre_ping=True)
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        await self.engine.dispose()

