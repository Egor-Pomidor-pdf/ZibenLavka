import React, { useEffect, useState } from 'react';
import cl from "./LkPage.module.css"
import { useNavigate } from 'react-router-dom';
import axios from 'axios';


interface InventoryItem {
  id: string;
  item_id: string;
  item_name: string;
  description: string;
  quantity: number;

}

interface userData {
  username: string,
  money: string,
  money_per_click: number,
  money_per_second: number,
  inventory: InventoryItem[],
}

const LkPage = () => {
  const navigate = useNavigate()

  const [quantities, setQuantities] = useState<Record<string, number>>({})
  const [costs, setCosts] = useState<Record<string, number>>({})

  const [userInfo, setUserInfo] = useState<userData>({
    username: "",
    money: "",
    money_per_click: 0,
    money_per_second: 0,
    inventory: [
      {
        id: "1",
        item_id: "101",
        item_name: "Золотой меч",
        description: "Острый меч из чистого золота",
        quantity: 3
      },
      {
        id: "2",
        item_id: "102",
        item_name: "Лечебное зелье",
        description: "Восстанавливает 50 HP",
        quantity: 10
      },
      {
        id: "3",
        item_id: "103",
        item_name: "Кожаный доспех",
        description: "Простая защита для новичков",
        quantity: 1
      },
      {
        id: "4",
        item_id: "104",
        item_name: "Магический свиток",
        description: "Позволяет выучить заклинание",
        quantity: 5
      },
      {
        id: "5",
        item_id: "105",
        item_name: "Редкий алмаз",
        description: "Драгоценный камень для крафта",
        quantity: 2
      }

    ]
  })

  const sellProduct = async (id: string,) => {
    try {
      const token = localStorage.getItem("accessToken");
      if (!token) {
        navigate("/login");
        return;
      }
      const selectedQuantity = quantities[id] || 1;
      const selectedCost = costs[id] || 1

      const response = await axios.post<string>("/api/v1/game/sell_auction/", {
        id: id,
        quantity: selectedQuantity,
        price: selectedCost,
      })
      console.log(`покупаем ${id}`);
      setUserInfo(prevCart => ({
        ...prevCart,
        inventory: prevCart.inventory.filter(item => item.id !== id)
      }
      )
      )
    } catch (error) {
      alert("Произошла ошибка при продаже")
      console.log(error);

    }

  }

  const handleQuantityChange = (id: string, value: number) => {
    setQuantities(prev => ({
      ...prev,
      [id]: value,
    }))
  }

  const handleCostsChange = (id: string, value: number) => {
    setCosts(prev => ({
      ...prev,
      [id]: value
    }))
  }

  const clickMoney = async () => {
    try {
      const token = localStorage.getItem("accessToken");
      if (!token) {
        navigate("/login");
        return;
      }
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      const clickResponse = await axios.post("api/v1/game/click/")
      await fetchData()
    } catch (error) {
      alert("Не удалось кликнуть")
      console.log(error);
    }
  }

  const fetchData = async () => {
    try {
      const token = localStorage.getItem("accessToken");
      if (!token) {
        navigate("/login");
        return;
      }

      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      const userResponse = await axios.get<userData>("/api/v1/game/info/")
      setUserInfo(userResponse.data);
    } catch (error) {
      console.log(error);
    }
  }

  useEffect(() => {
    fetchData();

    const intervalId = setInterval(fetchData, 1000);

    return () => clearInterval(intervalId);
  }, [navigate])

  return (
    <div className={cl.appContainer}>
      <div className={cl.container}>
        <h1 className={cl.title}>Личный кабинет</h1>

        <section className={cl.section}>
          <div className={cl.sectionHeader}>
            <h2 className={cl.sectionTitle}>Личные данные</h2>
          </div>

          <div className={cl.card}>
            <div className={cl.userInfoItem}>
              <span className={cl.infoLabel}>Логин:</span>
              <span className={cl.infoValue}>{userInfo.username}</span>
            </div>

            <div className={cl.userInfoItem}>
              <span className={cl.infoLabel}>Общее количество денег:</span>
              <span className={cl.infoValue}>{userInfo.money}</span>
            </div>

            <div className={cl.userInfoItem}>
              <span className={cl.infoLabel}>Монет за клик</span>
              <span className={cl.infoValue}>{userInfo.money_per_click}</span>
            </div>
            <div className={cl.userInfoItem}>
              <span className={cl.infoLabel}>Монет в секунду</span>
              <span className={cl.infoValue}>{userInfo.money_per_second}</span>
            </div>
          </div>
          <div className={cl.sectionClicker}>
            <h2 className={cl.sectionClicker__title}>Кликкер</h2>
            <button
              onClick={clickMoney}
              className={cl.sectionClicker__button}>НАЖАТЬ</button>
          </div>
          <div className={cl.sectionInventar}>
            {userInfo.inventory.map((item) => (
              <div className={cl.sectionInventar__product}>
                <h4 className={cl.sectionInventar__product__name}>{item.item_name}</h4>
                <p className={cl.sectionInventar__product__description}>{item.description}</p>
                <div className={cl.quantity}>{item.quantity}</div>
                <label htmlFor="quantity" className={cl.label}>количество на продажу*</label>
                <input
                  id="quantity"
                className={cl.input}

                  type="number"
                  min="1"
                  max={item.quantity}
                  value={
                    quantities[item.id] || 1
                  }
                  placeholder="Введите количество предметов на продажу"
                  onChange={(e) => handleQuantityChange(item.id, parseInt(e.target.value))}
                />
                <label htmlFor="cost" className={cl.label}>цена на продажу*</label>
                <input
                className={cl.input}
                id="cost"
                  type="number"
                  min="1"
                  value={
                    costs[item.id] || 1
                  }
                  placeholder="Введите цену на продажу"
                  onChange={(e) => handleCostsChange(item.id, parseInt(e.target.value))}
                />
                <button onClick={() => sellProduct(item.id)} className={cl.button__sell}>Выставить на аукцион</button>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
};

export default LkPage;
