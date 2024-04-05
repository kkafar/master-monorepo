import React, { useMemo } from 'react';
import './App.css';
import AppRouter from './route/AppRouter';
import ServerContext from './contexts/ServerContext';
import Server from './api/server';


function App() {
  const server = useMemo(() => new Server(), []);

  return (
    <ServerContext.Provider value={server}>
      <AppRouter />
    </ServerContext.Provider>
  );
}

export default App;
