import axios from "axios";
import { error } from "console";


const getAccessToken = () => localStorage.getItem("accessToken");
const getRefreshToken = () => localStorage.getItem("refreshToken");

axios.defaults.headers.common['Authorization'] = `Bearer ${getAccessToken()}`;


axios.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (
            error.response?.status === 401 &&
            !originalRequest._retry && getRefreshToken()
        ) {
            originalRequest._retry = true;
            try {
                const response = await axios.post("/api/v1/auth/token/refresh/", {
                    refresh: getRefreshToken(),
                })
                const newAccessToken = response.data.access;
                localStorage.setItem("accessToken", newAccessToken);
                axios.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`;
                originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
                return axios(originalRequest);
            } catch (refreshError) {
                console.error("Не удалось обновить токен", refreshError);
                localStorage.clear();
                window.location.href = "/login";
            }
        }
        throw error;
    }

)
