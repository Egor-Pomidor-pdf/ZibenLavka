import uuid
from django.db import models
from authentication.models import CustomUser

# Create your models here.


class Items(models.Model):
    name = models.CharField(max_length=100)
    cost = models.BigIntegerField()
    rarity = models.IntegerField()
    description = models.CharField(null=True)
    click_factor = models.IntegerField(default=0)
    timed_factor = models.IntegerField(default=1)
    image = models.ImageField(upload_to="items/", blank=True, null=True)

    def __str__(self):
        return self.name


class ShopItem(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    item = models.ForeignKey(Items, on_delete=models.CASCADE)


class Inventory(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    user = models.ForeignKey(CustomUser, null=False, on_delete=models.CASCADE)
    item = models.ForeignKey(Items, null=False, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False)

    def __str__(self):
        return f"{self.item.name}: {self.quantity}; owned by {self.user.username}"


class AuctionTable(models.Model):

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    item = models.ForeignKey(Items, on_delete=models.CASCADE)
    quantity = models.IntegerField(editable=True)
    price = models.IntegerField(editable=True)


def get_sum_of_rarieties() -> int:
    return Items.objects.aggregate(models.Sum("rarity"))["rarity__sum"]
