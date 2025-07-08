import React, { useEffect, useState } from 'react';
import { BrowserRouter } from 'react-router-dom';
import AppRouter from './API/Approuter';
import Navabar from './UI/Navabar/Navabar';
import "./style/App.css"
import { AuthContext } from './components/context';
// import Sidebar from './UI/Sidebar/Sidebar';
function App() {




  const [isAuth, setIsAuth] = useState(false);
  const [isLoading, setIsLoading] = useState(true)
  useEffect(() => {
    if (localStorage.getItem("auth")) {
      setIsAuth(true)
    }
  })

  return (
    <div className="App">

      <AuthContext.Provider value={{
        isAuth,
        setIsAuth,
      }}>
      <BrowserRouter>

        <Navabar />

        <AppRouter />

      </BrowserRouter>
    </AuthContext.Provider>

    </div>
  );
}

export default App;
