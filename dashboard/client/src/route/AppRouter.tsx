import React from "react";

import { BrowserRouter, Routes, Route } from 'react-router-dom';

import Home from '../pages/Home';

export default function AppRouter(): React.JSX.Element {
 return (
    <BrowserRouter>
      <Routes>
        <Route index element={<Home />} />
        <Route path='/home' element={<Home />} />
      </Routes>
    </BrowserRouter>
  );
}

