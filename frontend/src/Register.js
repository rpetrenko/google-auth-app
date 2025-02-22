import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './App.css';

function Register() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isEmailSent, setIsEmailSent] = useState(false);
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email, password }),
      });
      const data = await response.json();
      if (response.ok) {
        setIsEmailSent(true);
        setMessage('Check your email for a verification link.');
        setTimeout(() => navigate('/'), 3000); // redirect to home after 3 secs
      } else {
        setMessage(data.detail || 'Registration failed.');
      }
    } catch (error) {
      console.error('Registration error:', error);
      setMessage('An error occurred. Please try again.');
    }
  };

  return (
    <div className="App">
      <div className="login-container">
        <h2>Sign Up</h2>
        {!isEmailSent ? (
          <>
            <form className="local-login-form" onSubmit={handleRegister}>
              <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="login-input"
              />
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="login-input"
              />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="login-input"
              />
              <button type="submit" className="local-login-button">
                Sign Up
              </button>
            </form>
            <p>
              Already have an account? <a href="/">Log in</a>
            </p>
          </>
        ) : (
          <p className="message">
            {message} <a href="/">Back to Login</a>
          </p>
        )}
      </div>
    </div>
  );
}

export default Register;