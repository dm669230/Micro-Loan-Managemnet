import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from "./Login.jsx";
import Register from "./Register";
import Dashboard from "./Dashboard"
import LoanApplication from "./LoanApplication"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/apply-loan" element={<LoanApplication />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
