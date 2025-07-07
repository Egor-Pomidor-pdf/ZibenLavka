from datetime import timedelta
from rest_framework.permissions import IsAuthenticated
from adrf.views import APIView
from adrf import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from rest_framework import pagination
from django.http import HttpRequest
from django.utils import timezone
from django.db.models import F
from django.core.paginator import Paginator
from asgiref.sync import sync_to_async
from rest_framework.request import Request
from random import randint
from math import ceil
import logging

from authentication.models import CustomUser
from .models import *
from .tasks import click_money
from .serializers import *
from ziben.generics import ACreateAPIView
from ziben.settings import MIN_AMOUNT_OF_ITEMS_IN_SHOP, MAX_AMOUNT_OF_ITEMS_IN_SHOP

logger = logging.getLogger("game")

# Create your views here.


def _select_item_index(prefix: list[int]) -> int:
    weight = randint(1, prefix[-1])
    logger.info(weight)
    logger.debug("sdafasfd")
    logger.info(prefix)
    left, right = 0, len(prefix)

    while left < right:
        mid = (left + right) // 2

        left_val = prefix[mid - 1] if mid > 0 else -float("inf")
        right_val = prefix[mid] if mid < len(prefix) else float("inf")

        if left_val < weight <= right_val:
            return mid if mid > 0 else 0

        elif weight <= left_val:
            right = mid
        else:
            left = mid + 1

    return len(prefix) - 2


class AppleClicked(APIView):
    permission_classes = (IsAuthenticated,)

    async def post(self, request: HttpRequest):
        user: CustomUser = request.user
        click_money.delay(user.id, max(0, user.money_per_click))

        return Response({"message": "Task of click created"})


class InfoAPIView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserGameInfoSerializer

    async def get(self, request: Request):
        user = request.user
        serializer = self.get_serializer(user)
        data = await serializer.adata
        data["money_per_click"] = max(0, data["money_per_click"])
        data["money_per_second"] = max(0, data["money_per_second"])
        return Response(data)


class GetShopListAPIView(generics.ListAPIView):
    serializer_class = ShopItemSerializer
    permission_classes = (IsAuthenticated,)

    async def alist(self, request: HttpRequest):
        user: CustomUser = request.user

        if (
            not user.last_shop_update_date
            or timezone.now() - user.last_shop_update_date > timedelta(hours=6)
        ):

            if user.last_shop_update_date:
                await ShopItem.objects.filter(user=user).adelete()

            current_time = timezone.now()
            current_time -= timedelta(minutes=current_time.minute)
            current_time -= timedelta(seconds=current_time.second)
            current_time -= timedelta(microseconds=current_time.microsecond)
            current_time -= timedelta(hours=current_time.hour % 6)
            user.last_shop_update_date = current_time
            await user.asave()

            quantity = randint(MIN_AMOUNT_OF_ITEMS_IN_SHOP, MAX_AMOUNT_OF_ITEMS_IN_SHOP)

            count = await Items.objects.acount()
            prefix = [0] * (count + 1)
            ids = [0] * count

            items = [item async for item in Items.objects.aiterator()]

            for i, item in enumerate(items):
                prefix[i + 1] = prefix[i] + int(item.rarity)
                ids[i] = item.id

            print(prefix)

            result = []

            for _ in range(quantity):
                i = _select_item_index(prefix) - 1
                id = ids[i]
                item = await Items.objects.aget(id=id)
                result.append(await ShopItem.objects.acreate(user=user, item=item))
        else:
            result = await sync_to_async(list)(
                ShopItem.objects.select_related("item").filter(user=user)
            )

        return Response(await self.get_serializer(result, many=True).adata)

    def get_queryset(self):
        user = self.request.user
        return ShopItem.objects.filter(user=user)


class BuyItemAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    async def post(self, request):
        uuid = request.data["id"]
        user: CustomUser = request.user
        try:
            shopitem = await ShopItem.objects.select_related("item").aget(
                id=uuid, user=user
            )
        except:
            return Response(
                {"error": "invalid uuid"}, status=status.HTTP_400_BAD_REQUEST
            )

        now = timezone.now()

        current_money = int(user.money) + user.money_per_second * int(
            (now - user.time_money_last_earn).total_seconds()
        )

        if current_money < shopitem.item.cost:
            return Response(
                {"error": "not enough money"}, status=status.HTTP_400_BAD_REQUEST
            )

        user.time_money_last_earn = now
        user.money = str(current_money - shopitem.item.cost)

        try:
            inventoryitem = await Inventory.objects.aget(
                user=request.user, item=shopitem.item
            )
        except:
            inventoryitem = await Inventory.objects.acreate(
                user=request.user, item=shopitem.item, quantity=0
            )

        inventoryitem.quantity = F("quantity") + 1
        user.money_per_click += shopitem.item.click_factor
        user.money_per_second += shopitem.item.timed_factor

        await user.asave()
        await inventoryitem.asave()
        await shopitem.adelete()

        return Response({"message": "item bought succesfuly"})


class SellItemOnAuctionAPIView(ACreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SellItemSerializer
    queryset = AuctionTable.objects.all()

    async def post(self, request: Request):
        data = {**request.data}
        data["user_id"] = self.request.user.id

        serializer: SellItemSerializer = self.get_serializer(data=data)
        await serializer.ais_valid(raise_exception=True)
        await serializer.asell()

        return Response({"message": "inventory item is now on auction"})


class BuyItemAuctionAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    async def post(self, request: Request):
        data = {**request.data}
        data["user_id"] = self.request.user.id
        serializer = BuyItemAunctionSerializer(data=data)
        await serializer.ais_valid(raise_exception=True)
        await serializer.abuy()

        return Response({"message": "Items are successfuly bought"})


class RetriveFromAuctionAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    async def post(self, request: Request):
        data = {**request.data}
        data["user_id"] = self.request.user.id
        serializer = RetrieveFromAuctionItemSerializer(data=data)
        await serializer.ais_valid(raise_exception=True)
        await serializer.aretrieve()

        return Response({"message": "Items are successfuly retrieved"})


class UserAuctionAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    queryset = AuctionTable.objects.select_related("item").all()
    serializer_class = UserAuctionSerializer
    page_size = 10

    def filter_queryset(self, queryset):
        return (
            queryset.filter(user=self.request.user, quantity__gt=0)
            .annotate(total_price=F("quantity") * F("price"))
            .order_by("-total_price")
        )

    async def get(self, request, page_number):
        fqs = self.filter_queryset(self.queryset)
        count = await fqs.acount()
        start = (page_number - 1) * self.page_size
        if start > count:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        end = min(page_number * self.page_size, count)
        qs_slice = fqs[start:end]
        serializer = self.serializer_class(qs_slice, many=True)
        data = await serializer.adata

        ret = {
            "results": data,
            "count": count,
            "current_page": page_number,
            "total_pages": ceil(count / self.page_size),
        }

        if page_number > 1:
            ret["previous"] = f"http://api/v1/game/user_auction/?page={page_number - 1}"
        if page_number < ret["total_pages"]:
            ret["previous"] = f"http://api/v1/game/user_auction/?page={page_number + 1}"

        return Response(ret)


# Basically the same thing as User, but instead of filter, use exclude
class AuctionListAPIView(UserAuctionAPIView):

    queryset = AuctionTable.objects.select_related("item", "user").all()
    page_size = 20

    def filter_queryset(self, queryset):
        return (
            queryset.exclude(user=self.request.user)
            .filter(quantity__gt=0)
            .annotate(total_price=F("quantity") * F("price"))
            .order_by("-total_price")
        )


class BuyItemAuctionAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    async def post(self, request: Request):
        data = {**request.data}
        data["user_id"] = self.request.user.id
        serializer = BuyItemAunctionSerializer(data=data)
        await serializer.ais_valid()
        await serializer.abuy()

        return Response({"message": "Items are successfuly bought"})
