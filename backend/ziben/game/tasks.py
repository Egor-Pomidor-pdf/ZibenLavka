from django.db.models import F, Model
from celery import shared_task
from typing import Type, TypeVar
from importlib import import_module

from authentication.models import CustomUser
from game.models import *


DjangoModel = TypeVar("DjnagoModel", bound=Model)


def get_class_path(cls) -> str:
    return f"{cls.__module__}.{cls.__qualname__}"


@shared_task
def click_money(user_id: int, amount: int):
    user = CustomUser.objects.get(id=user_id)
    user.money = int(user.money) + amount
    user.save()


def make_transaction_item_between_users(
    model1: Type[DjangoModel],
    model2: Type[DjangoModel],
    itemholder_id,
    quantity: int,
    price: int,
    seller_id: int,
    receiver_id: int,
):
    transaction_item_between_users_task.delay(
        get_class_path(model1),
        get_class_path(model2),
        itemholder_id,
        quantity,
        price,
        seller_id,
        receiver_id,
    )


@shared_task
def transaction_item_between_users_task(
    model1_path: str,
    model2_path: str,
    itemholder_id,
    quantity: int,
    price: int,
    seller_id: int,
    receiver_id: int,
):
    """Transfer from model1 to model2 item in itemholder. user id's can be equal, then it's transaction between inventories: Inventory, Auction"""
    assert (
        model1_path != model2_path
    ), f"models must be different: {model1_path} = {model2_path}"
    module1_path, model1_name = model1_path.rsplit(".", 1)
    module2 = import_module(module1_path)
    model1: Type[DjangoModel] = getattr(module2, model1_name)

    module2_path, model2_name = model2_path.rsplit(".", 1)
    module2 = import_module(module2_path)
    model2: Type[DjangoModel] = getattr(module2, model2_name)

    assert issubclass(model1, (Model,)) and issubclass(model2, (Model,))

    receiver = CustomUser.objects.get(pk=receiver_id)

    seller = (
        CustomUser.objects.get(pk=seller_id) if seller_id != receiver_id else receiver
    )
    itemholder = model1.objects.get(pk=itemholder_id)
    item: Items = itemholder.item

    receiver.update_money()

    total_price = quantity * price

    if itemholder.quantity < quantity:
        return

    if receiver_id != seller_id:
        # Validating whether receiver has sufficient ammount of money
        if int(receiver.money) < total_price:
            return
        receiver.money = int(receiver.money) - total_price
        itemholder.quantity = F("quantity") - quantity
        seller.money = int(seller.money) + total_price

    try:
        inventory_slot = model2.objects.get(user=receiver, item=item)
        inventory_slot.quantity += quantity
        inventory_slot.save()
    except:
        if hasattr(model2, "price"):
            inventory_slot = model2.objects.create(
                user=receiver, item=item, quantity=quantity, price=price
            )
        else:
            inventory_slot = model2.objects.create(
                user=receiver, item=item, quantity=quantity
            )

    if receiver_id != seller_id:
        receiver.money_per_click = F("money_per_click") + quantity * item.click_factor
        receiver.money_per_second = F("money_per_second") + quantity * item.timed_factor
    else:
        if model1 == Inventory:
            receiver.money_per_click = (
                F("money_per_click") - quantity * item.click_factor
            )
            receiver.money_per_second = (
                F("money_per_second") - quantity * item.timed_factor
            )
        else:
            receiver.money_per_click = (
                F("money_per_click") + quantity * item.click_factor
            )
            receiver.money_per_second = (
                F("money_per_second") + quantity * item.timed_factor
            )

    receiver.save()

    print(itemholder.quantity)

    if itemholder.quantity == quantity:
        itemholder.delete()
    else:
        itemholder.save()

    if receiver_id != seller_id:
        seller.save()
