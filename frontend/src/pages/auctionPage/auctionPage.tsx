import React, { useEffect, useState } from 'react';
import cl from "./auctionPage.module.css"
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

interface generalItemInfo {
  id: string,
  name: string,
  description: string
}

interface concretInfoName {
  id: string,
  item: generalItemInfo,
  quantity: number,
  price: number,
  image: string
}

interface allPage {
  results: concretInfoName[],
  count: number,
  current_page: number,
  total_pages: number
}





const AuctionPage = () => {
  const [itemsListm, setItemsListm] = useState<concretInfoName[]>([
  ])
  const navigate = useNavigate()
  const [quantities, setQuantities] = useState<Record<string, number>>({})

  const buyProd = async (id: string) => {
    try {
      const token = localStorage.getItem("accessToken");
      if (!token) {
        navigate("/login");
        return;
      }

      const selectedQuantity = quantities[id] || 1;

      const response = await axios.post<string>("/api/v1/game/buy_auction/", { 
        id: id,
        quantity: selectedQuantity, 
      })
      console.log(`покупаем ${id}`);
      setItemsListm(prevCart => prevCart.filter(item => item.id !== id))

    } catch (error) {
      alert("Произошла ошибка при покупке")
      console.log(error);

    }

  }


  const handleQuantityChange = (id: string, value: number) => {
    setQuantities(prev => ({
      ...prev,
      [id]: value,
    }))
  }

  const fetchData = async () => {
    try {
      const token = localStorage.getItem("accessToken")
      if (!token) {
        navigate("/login")
      }
      const response = await axios.get<allPage>("/api/v1/game/auction/1/");
      setItemsListm(response.data.results)
    } catch {
      alert("Произошла ошибка при загрузке аукциона")
    }
  }


  useEffect(() => {
    fetchData();
  }, [])



  return (
    <div
      className={cl.auctionContainer}>
      <h1 className={cl.auctionContainer__title}>АУКЦИОН</h1>
      <div className={cl.auctionContainer__items}>
        {itemsListm.map((item) =>
          <div
            className={cl.auctionContainer__item}
          >
            <img className={cl.auctionContainer__item__image} src={item.image} alt="" />
            <span className={cl.auctionContainer__item__name}>{item.item.name}</span>
            <span className={cl.auctionContainer__item__price}>Цена: {item.item.name} Zcoins</span>
            <span className={cl.auctionContainer__item__quantity}>Количетсво: {item.quantity}</span>
            <span className={cl.auctionContainer__item__description}>{item.item.description}</span>
            <input 
            type="number"
            min="1"
            max={item.quantity}
            value={
              quantities[item.id] || 1
            }
            onChange={(e) => handleQuantityChange(item.id, parseInt(e.target.value))}
            />
            <button
              className={cl.prodItem__button}
              onClick={() => buyProd(item.id)}
            >
              Купить
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AuctionPage;