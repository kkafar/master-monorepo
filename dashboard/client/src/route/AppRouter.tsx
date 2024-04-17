import React from "react";

import { BrowserRouter, Routes, Route } from 'react-router-dom';

import Home from '../pages/Home';
import BatchDetails from '../pages/BatchDetails';

export default function AppRouter(): React.JSX.Element {
 return (
    <BrowserRouter>
      <Routes>
        <Route index element={<Home />} />
        <Route path='/home' element={<Home />} />
        <Route path='/details/:batchName' element={<BatchDetails />} />
      </Routes>
    </BrowserRouter>
  );
}

