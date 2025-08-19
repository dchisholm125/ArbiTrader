class Redis:
    async def xadd(self, *args, **kwargs):
        raise NotImplementedError

    async def xread(self, *args, **kwargs):
        raise NotImplementedError
