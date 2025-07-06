import { FC } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import MainPage from "../pages/MainPage/MainPage";
import LkPage from "../pages/LkPage/LkPage";
import LoginPage from "../pages/LoginPage/LoginPage";
import RegPage from "../pages/RegPage/RegPage";
import TapPage from "../pages/TapPage/TapPage";
import EmailConfirmationPage from "../pages/EmailConfirmationPage/EmailConfirmationPage";


const AppRouter:FC = () => {
    const routes = [
      { path: "/", element: <MainPage /> },
      { path: "/lkabinet", element: <LkPage /> },
      { path: "/login", element: <LoginPage /> },
      { path: "/reg", element: <RegPage /> },
      { path: "/tap", element: <TapPage /> },
      {path: "/accounts/register/:uidb64/:token/", element: <EmailConfirmationPage/>}
    ]
    return (
      
      <Routes>
       {routes.map((route, index) => (
        <Route key={index} path={route.path} element={route.element}/>
       ))}
      </Routes>
    );
  };

  export default AppRouter;