import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from "./Login.jsx";
import Register from "./Register";
import TaskPage from "./TaskPage";


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/tasks" element={<TaskPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
