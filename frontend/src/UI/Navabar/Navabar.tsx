import React, { FC } from 'react';
import cl from "./Navabar.module.css"
import { Link } from 'react-router-dom';

const Navabar: FC = () => {
  return (
    <div className={cl.navabar}>
      <Link
        className={`${cl.navabar__links__item} ${cl.navabar__links__item_reg}`}
        to="/"
      >
          дом
      </Link>
      <Link
        className={`${cl.navabar__links__item} ${cl.navabar__links__item_reg}`}
        to="/lkabinet"
      >
        Личный кабинет
      </Link>
      <Link
        className={`${cl.navabar__links__item} ${cl.navabar__links__item_reg}`}
        to="/login"
      >
        Вход
      </Link>
      <Link
        className={`${cl.navabar__links__item} ${cl.navabar__links__item_reg}`}
        to="/auction"
      >
        Аукцион
      </Link>
      <Link
        className={`${cl.navabar__links__item} ${cl.navabar__links__item_reg}`}
        to="/myAuction"
      >
        МойАукцион
      </Link>
    </div>
  );
};


export default Navabar;