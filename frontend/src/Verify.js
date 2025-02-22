import React, { useEffect, useState } from 'react';
import './App.css';
import { useSearchParams, useNavigate } from 'react-router-dom';

function Verify() {
  const [message, setMessage] = useState('Verifying your email...');
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const token = searchParams.get('token');
    if (token) {
      verifyEmail(token);
    } else {
      setMessage('No verification token provided.');
    }
  }, [searchParams]);

  const verifyEmail = async (token) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/verify?token=${token}`, {
        method: 'GET',
      });
      const data = await response.json();
      if (response.ok) {
        setMessage('Email verified successfully! Redirecting to login...');
        setTimeout(() => navigate('/'), 2000); // Redirect after 2 seconds
      } else {
        setMessage(data.detail || 'Verification failed.');
      }
    } catch (error) {
      console.error('Verification error:', error);
      setMessage('An error occurred during verification.');
    }
  };

  return (
    <div className="App">
      <div className="login-container">
        <p className="message">{message}</p>
      </div>
    </div>
  );
}

export default Verify;