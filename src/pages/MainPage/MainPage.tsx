import React, { FC, useEffect, useState } from 'react';
import cl from "./MainPage.module.css"
import { useNavigate } from 'react-router-dom';
import head from "./images/Web_Photo_Editor.jpg"
import def from "./images/Снимок экрана 2025-07-03 в 22.59.42.png"
import axios from 'axios';
// import 'bootstrap/dist/css/bootstrap.min.css'; 


interface Product {
  id: string,
  item_id: number,
  name: string,
  cost: number,
  description: string,
}
const MainPage: FC = () => {
  const [cart, setCart] = useState<Product[]>([
  ]);



  const buyProd = async (id: string) => {
    try {

      const response = await axios.post<string>("/api/v1/game/buy/", { id: id })
      console.log(`покупаем ${id}`);

      setCart(prevCart => prevCart.filter(item => item.id !== id))

    } catch (error) {
      alert("Произошла ошибка при покупке")
      console.log(error);

    }

  }



  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await axios.get("/api/v1/game/shop/");
        setCart(response.data)
      } catch (error) {
        console.log(error);
      }
    }

    fetchProducts();
  }, [])

  return (

    <div className={cl.main}>
      <section className={cl.header}>
        <div className={cl.container}>
          <img className={cl.header__image} src={head} alt="" />
        </div>
      </section>
      <section className={cl.products}>
        <div className={cl.container}>
          {cart.map((prod) => (
            <div
              key={prod.item_id}
              className={`${cl.prodItem}`}
            >
              <div className={cl.prodItem__info}>
                <span>
                  {prod.name}
                </span>
                <img className={cl.prodItem__img} src={def} />
                <div className={cl.prodItem__text}>
                  <span>
                    Цена: {prod.cost} Zcoins
                  </span>
                  <span className={cl.prodItem__text__description}>
                    {prod.description}
                  </span>

                </div>

              </div>
              <button
                className={cl.prodItem__button}
                onClick={() => buyProd(prod.id)}
              >
                Купить
              </button>
            </div>
          ))}
        </div>

      </section>

    </div>


  )
}

export default MainPage;
