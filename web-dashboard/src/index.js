import React from "react";
import { createRoot } from "react-dom/client";
import WrappedApp from "./App.jsx";

const root = createRoot(document.getElementById("root"));
root.render(<WrappedApp />);
