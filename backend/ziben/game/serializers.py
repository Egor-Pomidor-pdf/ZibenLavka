from django.db.models import F
from django.utils import timezone
from adrf.fields import SerializerMethodField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
import logging

from .models import *
from .tasks import make_transaction_item_between_users
from authentication.models import CustomUser
from ziben.base_serializer import BaseAsyncSerializer

logger = logging.getLogger("game")


class ItemSerializer(BaseAsyncSerializer):
    class Meta:
        model = Items
        fields = "__all__"


class InventoryItemSerializer(BaseAsyncSerializer):
    item_id = serializers.UUIDField(source="item.id")
    item_name = serializers.CharField(source="item.name")
    description = serializers.CharField(source="item.description")
    image = serializers.ImageField(source="item.image", required=False, allow_null=True)

    class Meta:
        model = Inventory
        fields = ("id", "item_id", "item_name", "description", "quantity", "image")


class ShopItemSerializer(BaseAsyncSerializer):
    # user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    item_id = serializers.IntegerField(source="item.id")
    name = serializers.CharField(source="item.name")
    cost = serializers.IntegerField(source="item.cost")
    description = serializers.CharField(source="item.description")
    image = serializers.ImageField(source="item.image", required=False, allow_null=True)

    class Meta:
        model = ShopItem
        fields = ("id", "item_id", "name", "cost", "description", "image")


class UserGameInfoSerializer(BaseAsyncSerializer):
    money = serializers.SerializerMethodField("get_money")
    inventory = SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "money",
            "money_per_click",
            "money_per_second",
            "inventory",
        )

    async def avalidate(self, data):
        data["money_per_click"] = max(0, data["money_per_click"])
        data["money_per_second"] = max(0, data["money_per_second"])
        logger.info(data)
        return await super().avalidate(data)

    def get_money(self, user: CustomUser) -> str:
        return str(user.get_current_money())

    async def get_inventory(self, user: CustomUser) -> list:
        queryset = Inventory.objects.select_related("item").filter(user=user)
        inventory = [item async for item in queryset]
        serializer = InventoryItemSerializer(inventory, many=True)
        data = await serializer.adata
        return data


class SellItemSerializer(BaseAsyncSerializer):

    id = serializers.UUIDField()
    user_id = serializers.IntegerField()

    class Meta:
        model = AuctionTable
        fields = ["user_id", "id", "quantity", "price"]

    async def avalidate(self, data):
        self._errors = []
        if data["quantity"] <= 0:
            self._errors.append({"quantity": "quantity should be positive"})
        if data["price"] <= 0:
            self._errors.append({"price": "price should be positive"})

        try:
            self.user: CustomUser = await CustomUser.objects.aget(pk=data["user_id"])
        except:
            self._errors.append({"user": "invalid user_id"})

        try:
            self.invitem = await Inventory.objects.select_related("item").aget(
                pk=data["id"], user_id=data["user_id"]
            )
            if self.invitem.quantity < data["quantity"]:
                self._errors.append({"user": "insufficient amount of id item"})

        except:
            self._errors.append({"inventory_item": "invalid inventory_item_id"})

        if self._errors:
            raise ValidationError(detail=self._errors)

        return data

    async def asell(self):
        assert hasattr(
            self, "_errors"
        ), "You must call `.ais_valid()` before calling `.asell()`."
        validated_data = self.validated_data
        await make_transaction_item_between_users(
            Inventory,
            AuctionTable,
            self.invitem,
            validated_data["quantity"],
            validated_data["price"],
            validated_data["user_id"],
            validated_data["user_id"],
        )
        # try:
        #     auctionitem = await AuctionTable.objects.select_related("item").aget(
        #         userd=self.user, item=self.invitem.item, price=validated_data["price"]
        #     )
        #     auctionitem.quantity = F("quantity") + validated_data["quantity"]
        #     await auctionitem.asave()
        # except:
        #     auctionitem = await AuctionTable.objects.select_related("item").acreate(
        #         user=self.user,
        #         item=self.invitem.item,
        #         quantity=validated_data["quantity"],
        #         price=validated_data["price"],
        #     )

        # if self.invitem.quantity == validated_data["quantity"]:
        #     await self.invitem.adelete()
        # else:
        #     self.invitem.quantity = F("quantity") - validated_data["quantity"]
        #     await self.invitem.asave()

        # self.user.money_per_click = (
        #     F("money_per_click")
        #     - validated_data["quantity"] * self.invitem.item.click_factor
        # )

        # self.user.update_money()
        # self.user.money_per_second = (
        #     F("money_per_second")
        #     - validated_data["quantity"] * self.invitem.item.timed_factor
        # )

        # await self.user.asave()

        # return auctionitem


class BuyItemAunctionSerializer(BaseAsyncSerializer):

    user_id = serializers.IntegerField()
    id = serializers.UUIDField()

    class Meta:
        model = AuctionTable
        fields = ["id", "user_id", "quantity"]

    async def avalidate(self, data):
        print("validation called")
        self._errors = []
        if data["quantity"] <= 0:
            self._errors.append({"quantity": "quantity should be positive"})

        try:
            self.user: CustomUser = await CustomUser.objects.aget(pk=data["user_id"])
        except:
            self._errors.append({"user": "invalid user_id"})

        try:
            self.slot = await AuctionTable.objects.select_related("item").aget(
                pk=data["id"], user_id=data["user_id"]
            )
            if self.slot.quantity < data["quantity"]:
                self._errors.append({"aucitem": "insufficient amount of id item"})

        except:
            self._errors.append({"aucitem": "invalid aucitem id"})

        if self._errors:
            raise ValidationError(self._errors)

        print("returned")

        return data
        # self._errors = []
        # print(data)
        # if data["quantity"] <= 0:
        #     print("negative")
        #     self._errors.append({"quantity": "quantity should be positive"})

        # try:
        #     self.user: CustomUser = await CustomUser.objects.aget(pk=data["user_id"])
        # except:
        #     self._errors.append({"user": "invalid user_id"})
        #     self.user = None

        # try:
        #     self.slot = await AuctionTable.objects.select_related("user", "item").aget(
        #         id=data["id"]
        #     )
        #     if (
        #         self.user
        #         and self.user.get_current_money() < self.slot.price * data["quantity"]
        #     ):
        #         self._errors.append({"auctionitem": "Insufficient amount of funds"})

        #     if self.user and self.user.id == self.slot.user.id:
        #         self._errors.append({"user": "You can't buy your own items"})

        #     if self.slot.quantity < data["quantity"]:
        #         self._errors.append({"auctionitem": "wrong number of items"})

        # except Exception as e:
        #     self._errors.append({"auctionitem": "Item of Auction is not found"})
        #     self.slot = None

        # print(len(self._errors))
        # print(data)
        # if self._errors:
        #     raise ValidationError(self._errors)

        # return data

    async def abuy(self) -> None:

        assert hasattr(
            self, "_errors"
        ), "You must call `.ais_valid()` before calling `.abuy()`."

        data = self.validated_data
        await make_transaction_item_between_users(
            AuctionTable,
            Inventory,
            self.slot,
            data["quantity"],
            self.slot.price,
            self.slot.user.id,
            self.user.id,
        )

        # self.user.update_money()

        # quantity = validated_data["quantity"]
        # price = quantity * self.slot.price
        # item = self.slot.item
        # seller = self.slot.user

        # self.user.money = int(self.user.money) - price
        # self.slot.quantity -= quantity
        # seller.money = int(self.slot.user.money) + price

        # try:
        #     inventory_slot = await Inventory.objects.aget(user=self.user, item=item)
        #     inventory_slot.quantity += quantity
        #     await inventory_slot.asave()
        # except:
        #     inventory_slot = await Inventory.objects.acreate(
        #         user=self.user, item=item, quantity=quantity
        #     )

        # self.user.money_per_click += quantity * item.click_factor
        # self.user.money_per_second += quantity * item.timed_factor

        # await seller.asave()

        # if self.slot.quantity == 0:
        #     await self.slot.adelete()
        # else:
        #     await self.slot.asave()

        # await self.user.asave()


class RetrieveFromAuctionItemSerializer(BaseAsyncSerializer):

    id = serializers.UUIDField()
    user_id = serializers.IntegerField()

    class Meta:
        model = AuctionTable
        fields = ["user_id", "id", "quantity"]

    async def avalidate(self, data):
        self._errors = []
        if data["quantity"] <= 0:
            self._errors.append({"quantity": "quantity should be positive"})

        try:
            self.user: CustomUser = await CustomUser.objects.aget(pk=data["user_id"])
        except:
            self._errors.append({"user": "invalid user_id"})

        try:
            self.aucitem = await AuctionTable.objects.select_related("item").aget(
                pk=data["id"], user_id=data["user_id"]
            )
            if self.aucitem.quantity < data["quantity"]:
                self._error.append(
                    {"inventory_item": "insufficient amount of inventory_item_id item"}
                )

        except:
            self._errors.append({"inventory_item": "invalid inventory_item_id"})
        if self._errors:
            raise ValidationError(self._errors)
        return data

    async def aretrieve(self):
        assert hasattr(
            self, "_errors"
        ), "You must call `.ais_valid()` before calling `.asell()`."
        assert len(self._errors) == 0, "errors happened"
        validated_data = self.validated_data
        await make_transaction_item_between_users(
            AuctionTable,
            Inventory,
            self.aucitem,
            validated_data["quantity"],
            None,
            validated_data["user_id"],
            validated_data["user_id"],
        )


class UserAuctionSerializer(BaseAsyncSerializer):
    item = serializers.SerializerMethodField()
    image = serializers.ImageField(source="item.image", required=False, allow_null=True)

    class Meta:
        model = AuctionTable
        fields = ["id", "item", "quantity", "price", "image"]

    def get_item(self, auctionitem: AuctionTable):
        item = auctionitem.item
        return {
            "id": item.id,
            "name": item.name,
            "description": item.description,
        }


class AuctionSerializer(BaseAsyncSerializer):
    item = serializers.SerializerMethodField()
    username = serializers.CharField(source="user.name")
    image = serializers.ImageField(source="item.image", required=False, allow_null=True)

    class Meta:
        model = AuctionTable
        fields = ["id", "item", "user", "quantity", "price", "image"]

    def get_item(self, auctionitem: AuctionTable):
        item = auctionitem.item
        return {
            "id": item.id,
            "name": item.name,
            "description": item.description,
        }
