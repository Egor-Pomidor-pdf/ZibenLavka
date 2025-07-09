import React, { useEffect, useState } from 'react';
import cl from "./auctionPage.module.css"
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import def from "../MainPage/images/tf.png"

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
    {
      id: "1",
      item: {
        id: "101",
        name: "Золотой меч дракона",
        description: "Легендарный меч, выкованный из чешуи древнего дракона"
      },
      quantity: 3,
      price: 2500,
      image: `${def}`
    },
    {
      id: "2",
      item: {
        id: "102",
        name: "Эликсир бессмертия",
        description: "Дарует временную неуязвимость на 30 секунд"
      },
      quantity: 5,
      price: 1500,
      image: "https://example.com/potion.jpg"
    },
    {
      id: "3",
      item: {
        id: "103",
        name: "Кольцо маны",
        description: "Увеличивает максимальный запас маны на 20%"
      },
      quantity: 1,
      price: 3200,
      image: "https://example.com/ring.jpg"
    },
    {
      id: "4",
      item: {
        id: "104",
        name: "Древний свиток телепортации",
        description: "Позволяет мгновенно переместиться в любую точку мира"
      },
      quantity: 2,
      price: 5000,
      image: "https://example.com/scroll.jpg"
    },
    {
      id: "5",
      item: {
        id: "105",
        name: "Шлем повелителя демонов",
        description: "Защищает от темной магии и увеличивает интеллект"
      },
      quantity: 1,
      price: 4200,
      image: "https://example.com/helmet.jpg"
    },
    {
      id: "6",
      item: {
        id: "106",
        name: "Мешок алмазов",
        description: "Набор из 10 редких алмазов для крафта"
      },
      quantity: 7,
      price: 1800,
      image: "https://example.com/diamonds.jpg"
    },
    {
      id: "7",
      item: {
        id: "107",
        name: "Посох ледяного короля",
        description: "Позволяет вызывать ледяные бури"
      },
      quantity: 1,
      price: 3800,
      image: "https://example.com/staff.jpg"
    },
    {
      id: "8",
      item: {
        id: "108",
        name: "Яйцо феникса",
        description: "Можно вывести верного спутника-феникса"
      },
      quantity: 1,
      price: 7500,
      image: "https://example.com/egg.jpg"
    }
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

  // const fetchData = async () => {
  //   try {
  //     const token = localStorage.getItem("accessToken")
  //     if (!token) {
  //       navigate("/login")
  //     }
  //     const response = await axios.get<allPage>("/api/v1/game/auction/1/");
  //     setItemsListm(response.data.results)
  //   } catch {
  //     alert("Произошла ошибка при загрузке аукциона")
  //   }
  // }


  // useEffect(() => {
  //   fetchData();
  // }, [])



  return (
    <div
      className={cl.auctionContainer}>
      <h1 className={cl.auctionContainer__title}>АУКЦИОН</h1>
      <div className={cl.auctionContainer__items}>
        {itemsListm.map((item) =>
          <div 
            key={item.item.id}
            className={cl.auctionContainer__item}
          >
            <img className={cl.auctionContainer__item__image} src={item.image} alt="" />
            <span className={cl.auctionContainer__item__name}>{item.item.name}</span>
            <span className={cl.auctionContainer__item__cost}>Цена: {item.price} Zcoins</span>
            <span className={cl.auctionContainer__item__quantity}>Количетсво: {item.quantity}</span>
            <span className={cl.auctionContainer__item__description}>{item.item.description}</span>
            <label htmlFor="quantity" className={cl.label}>количество на продажу*</label>
            <input 
            id="quantity"
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