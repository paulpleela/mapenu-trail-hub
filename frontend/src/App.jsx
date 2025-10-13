import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Dashboard from "./components/Dashboard";
import MeasureGPX from "./components/MeasureGPX";
import "./App.css";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/measure" element={<MeasureGPX />} />
      </Routes>
    </Router>
  );
}

export default App;
