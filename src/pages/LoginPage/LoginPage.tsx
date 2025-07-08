import axios from 'axios';
import React, { useContext, useState } from 'react';
import { AuthContext } from '../../components/context';
import { useNavigate } from 'react-router-dom';
import cl from "./LoginPage.module.css"
import { EventType } from '@testing-library/dom';

interface formData {
  email: string,
  password: string,
}

interface LoginResponse {
  access: string;
  refresh: string;
}


const LoginPage = () => {
  const navigate = useNavigate()
  const { isAuth, setIsAuth } = useContext<any>(AuthContext);
  const username = useState("")
  const password = useState("")
  const exitFromAccount = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    setIsAuth(false);
    localStorage.removeItem("auth");
    localStorage.removeItem("accessToken");
    // localStorage.removeItem("userId");
    // localStorage.removeItem("is_specialist");
    delete axios.defaults.headers.common['Authorization'];
    navigate("/login");
  }


  const [userData, setUserData] = useState<formData>(
    {
      email: "",
      password: ""
    }
  )

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setUserData(prev => ({
      ...prev,
      [name]: value
    }))
  }


  const loginFormSend = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const response = await axios.post<LoginResponse>("/api/v1/auth/login/", userData, {
        headers: {
          "Content-Type": "application/json",
        }
      })
      const accessToken = response.data.access
      const refreshToken = response.data.refresh

      console.log("Вход совершил");
      
      if (accessToken) {
        console.log("Вход успешно совершен");
        setIsAuth(true);
        localStorage.setItem("auth", "true");
        localStorage.setItem("accessToken", accessToken);
        localStorage.setItem("refreshToken", refreshToken);

        // localStorage.setItem("refreshToken", refreshToken); 
        axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
        navigate("/");
      }
    } catch (error) {
      console.log(error);
      alert("Произошла ошибка")
    }
  }


  return (
    <div className={cl.background}>
      <div className={cl.container}>
        <div className={cl.header}>
          <h1 className={cl.title}>Добро пожаловать</h1>
          <p className={cl.subtitle}>Введите ваши данные для входа</p>
        </div>

        <form onSubmit={loginFormSend} className={cl.form}>
          <div className={cl.inputGroup}>
            <label htmlFor="email" className={cl.label}>Логин</label>
            <input
              id="email"
              name="email"
              className={cl.input}
              value={userData.email}
              onChange={handleChange}
              type="text"
              placeholder="Введите вашу почту"
              required
            />
          </div>

          <div className={cl.inputGroup}>
            <label htmlFor="password" className={cl.label}>Пароль</label>
            <input
              name="password"
              id="password"
              className={cl.input}
              value={userData.password}
              onChange={handleChange}
              type="password"
              placeholder="Введите ваш пароль"
              required
            />
          </div>



          <button
            type="submit"
            className={cl.button}
          >
            "Войти"
          </button>
        </form>

        {isAuth && (
          <button
            onClick={exitFromAccount}
            className={`${cl.button} ${cl.exitButton}`}
          >
            Выйти из аккаунта
          </button>
        )}

        <div className={cl.footer}>
          <p className={cl.footerText}>Нет аккаунта? <a href="/reg" className={cl.link}>Зарегистрируйтесь</a></p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;