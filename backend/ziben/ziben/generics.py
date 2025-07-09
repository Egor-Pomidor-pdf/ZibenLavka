from .mixins import *
from adrf import generics


class ACreateAPIView(ACreateMixin, generics.GenericAPIView):
    async def post(self, request, data=None, *args, **kwargs):
        return await self.acreate(request, data=data, *args, **kwargs)
