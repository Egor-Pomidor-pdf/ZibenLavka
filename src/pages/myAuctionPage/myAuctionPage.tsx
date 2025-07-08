import axios from 'axios';
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import cl from "./myAuctionPage.module.css"


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




const MyAuctionPage = () => {
  const [cart, setCart] = useState<concretInfoName[]>([])
  const navigate = useNavigate()
  const [quantities, setQuantities] = useState<Record<string, number>>({})
  


  const returnProduct = async (id: string) => {
    try {
      const selectedQuantity = quantities[id] || 1;
      const response = await axios.post<string>("api/v1/game/retrieve_auction/", { 
        id: id,
        quantity: selectedQuantity, 
      })
      console.log(`возвращаем ${id}`);
      setCart(prevCart => prevCart.filter(item => item.id !== id))

    } catch (error) {
      alert("Произошла ошибка при возврате")
      console.log(error);

    }

  }

 
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const token = localStorage.getItem("accessToken");
      if (!token) {
        navigate("/login");
        return;
      }
        const response = await axios.get<allPage>("/api/v1/game/user_auction/1/");
        setCart(response.data.results)
      } catch (error) {
        console.log(error);
      }
    }

    fetchProducts();
  }, [])

  

  return (<div className={cl.appContainer}>
    <div className={cl.container}>
      <h1 className={cl.title}>Мои аукционы</h1>

      <section className={cl.section}>
        <div className={cl.sectionHeader}>
          <h2 className={cl.sectionTitle}>Текущие лоты</h2>
        </div>

        <div className={cl.auctionItems}>
          {cart.map((item) => (
            <div key={item.id} className={cl.auctionItem}>
              <img 
                src={item.image} 
                alt={item.item.name} 
                className={cl.auctionItemImage}
              />
              <div className={cl.auctionItemInfo}>
                <h3 className={cl.auctionItemName}>{item.item.name}</h3>
                <p className={cl.auctionItemDescription}>{item.item.description}</p>
                <div className={cl.auctionItemDetails}>
                  <span>Цена: {item.price}</span>
                  <span>Количество: {item.quantity}</span>
                </div>
              </div>
              <div className={cl.auctionItemActions}>
                <input
                  type="number"
                  min="1"
                  max={item.quantity}
                  value={quantities[item.id] || 1}
                  onChange={(e) => 
                    setQuantities(prev => ({
                      ...prev,
                      [item.id]: parseInt(e.target.value)
                    }))
                  }
                  className={cl.quantityInput}
                />
                <button 
                  onClick={() => returnProduct(item.id)}
                  className={cl.returnButton}
                >
                  Вернуть
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  </div>
);
};

export default MyAuctionPage;