from rest_framework.response import Response
from rest_framework import status
from adrf.mixins import get_data
from adrf import mixins


class ACreateMixin(mixins.CreateModelMixin):
    async def acreate(self, request, data=None, *args, **kwargs):
        in_data = data if data else request.data
        serializer = self.get_serializer(data=in_data)
        await serializer.ais_valid(raise_exception=True)
        await self.perform_acreate(serializer)
        data = await get_data(serializer)
        headers = self.get_success_headers(data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class ListModelMixin(mixins.ListModelMixin):
    """
    List a queryset.
    """

    async def alist(self, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = await self.apaginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = await get_data(serializer)
            return await self.get_apaginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data = await get_data(serializer)
        return Response(data, status=status.HTTP_200_OK)
