import React from "react";
import Server from "../api/server";

const ServerContext = React.createContext<Server>(new Server());

export default ServerContext;
