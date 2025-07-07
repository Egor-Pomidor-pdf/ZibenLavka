from django.urls import path
from .views import *

urlpatterns = [
    path("click/", AppleClicked.as_view()),
    path("info/", InfoAPIView.as_view()),
    path("shop/", GetShopListAPIView.as_view()),
    path("buy/", BuyItemAPIView.as_view()),
    path("sell_auction/", SellItemOnAuctionAPIView.as_view()),
    path("buy_auction/", BuyItemAuctionAPIView.as_view()),
    path("retrieve_auction/", RetriveFromAuctionAPIView.as_view()),
    path("user_auction/<int:page_number>/", UserAuctionAPIView.as_view()),
    path("auction/<int:page_number>/", AuctionListAPIView.as_view()),
]
