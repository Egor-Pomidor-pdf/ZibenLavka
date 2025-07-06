import React, { useState } from 'react';
import cl from "./RegPage.module.css"
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

interface formD {
    email: string,
    username: string,
    password: string
}

const RegPage = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState<formD>(
        {
            email: "",
            username: "",
            password: ""
        }
    )

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const {name, value} = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }))
    }

    const handleSubmit = async (e: React.ChangeEvent<HTMLFormElement>) => {
        e.preventDefault();
        console.log("");
        
        try {
            const response = await axios.post<formD>("/api/v1/auth/register/", formData, {
                headers: {
                  'Content-Type': 'application/json',
                  'Accept': 'application/json'
                }
              })
            console.log("Succes");
            navigate("/login")
        } catch(er) {
            console.log(er);
            
        }
    }

    return (
        <div className={cl.background}>
            <div className={cl.container}>
                <div className={cl.header}>
                    <h1 className={cl.title}>Создайте аккаунт</h1>
                    <p className={cl.subtitle}>Заполните форму для регистрации</p>
                </div>
                <form onSubmit={handleSubmit} action="" className={cl.form}>
                   
                    <div className={cl.inputGroup}>
                            <label htmlFor="username" className={cl.label}>username*</label>
                            <input
                            id="username"
                             name="username"
                             className={cl.input}
                             value={formData.username}
                             onChange={handleChange}
                             type="text"
                             placeholder="Ваш логин"
                             required
                             />
                    </div>
                    <div className={cl.inputGroup}>
                            <label htmlFor="password" className={cl.label}>username*</label>
                            <input
                            id="password"
                             name="password"
                             className={cl.input}
                             value={formData.password}
                             onChange={handleChange}
                             type="text"
                             placeholder="Ваш пароль"
                             required
                             />
                    </div>
                    <div className={cl.inputGroup}>
                            <label htmlFor="email" className={cl.label}>username*</label>
                            <input
                            id="email"
                             name="email"
                             className={cl.input}
                             value={formData.email}
                             onChange={handleChange}
                            type="text"
                             placeholder="Ваша почта"
                             required
                             />
                    </div>

                    <button 
                    type="submit"
                    className={cl.button}
                    >Зарегистрироваться</button>
                </form>


            </div>
        </div>
    );
};

export default RegPage;

// {email, username, password}