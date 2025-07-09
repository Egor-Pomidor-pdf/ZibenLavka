import axios, { AxiosError } from 'axios';
import React, { useEffect, useState } from 'react';
import { ErrorResponse, useNavigate, useParams } from 'react-router-dom';
import cl from "./EmailConfirmationPage.module.css"

const EmailConfirmationPage = () => {
    const { uidb64, token } = useParams();
    const navigate = useNavigate();
    const [isError, setIsError] = useState<boolean>(true)

    const [status, setStatus] = useState("loading")
    const [message, setMessage] = useState<string>("")



    useEffect(() => {
        const confirmEmail = async () => {
            try {
                const response = await axios.post('/api/v1/auth/verify-email/', { uidb64, token }, {
                    headers: {
                        'Authorization': undefined 
                      }
                }
                    
                )
                if (response.data.message === "User is registered") {
                    setMessage("Email подтверждён!");
                    navigate('/login');
                }
            } catch (error: any) {
                console.log(error.message);

            }
        }
        confirmEmail(); 
    }, [])



    return (
        <div
            style={{
                maxWidth: '500px',
                margin: '2rem auto',
                marginTop: "100px",
                padding: '2rem',
                textAlign: 'center',
                backgroundColor: isError ? '#ffeeee' : '#f0fff0',
                border: `1px solid ${isError ? '#ff0000' : '#00aa00'}`,
                borderRadius: '8px'
            }}>
            <h2>{isError ? 'Ошибка' : 'Успех'}</h2>
            <p>{message}</p>

            {isError && (
                <button
                    onClick={() => navigate('/reg')}
                    style={{
                        padding: '0.5rem 1rem',
                        backgroundColor: '#007bff',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer'
                    }}
                >
                    Вернуться к регистрации
                </button>
            )}
        </div>
    );

};

export default EmailConfirmationPage;


// if (error.response) {
//     switch (error.response.data.error) {
//         case "Invalid token":
//             setMessage("Неверная ссылка подтверждения");
//             break;
//         case "user not found":
//             setMessage("Пользователь не найден");
//             break;
//         default:
//             setMessage(`Ошибка: ${error.response.data.error || "Unknown error"}`);
//     }
// } else {
//     // Ошибки сети (сервер не ответил)
//     setMessage("Ошибка соединения с сервером");
// }