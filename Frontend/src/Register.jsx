import { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Register() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password_hash, setPassword] = useState('');
  const navigate = useNavigate();


  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:8000/auth/registration', { name, email, password_hash });
      alert('Registered Successfully!');
      localStorage.removeItem('access_token');
      navigate('/login');
    } catch (err) {
      alert('Registration failed');
    }
  };

  return (
    <div className="register-page">
      <h2>Register</h2>
      <form onSubmit={handleRegister}>
      <input type="text" placeholder="name" onChange={(e) => setName(e.target.value)} required />
      <input type="text" placeholder="email" onChange={(e) => setEmail(e.target.value)} required />
        <input type="text" placeholder="password" onChange={(e) => setPassword(e.target.value)} required />
        <button onClick={handleRegister} type="submit">Register</button>
      </form>
      <p>Already have an account? <a href="/login">Login</a></p>
    </div>
  );
}

export default Register;
