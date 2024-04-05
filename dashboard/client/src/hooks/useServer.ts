import React from "react";
import Server from "../api/server";
import ServerContext from "../contexts/ServerContext";

export function useServer(): Server | undefined {
  const server = React.useContext(ServerContext);

  if (!server) {
    console.error("Failed to resolve context instance. Make sure your component hierarchy is wrapped in ServerContext.");
  }

  return server;
}

