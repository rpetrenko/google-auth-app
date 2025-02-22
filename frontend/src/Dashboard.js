import React from 'react';
import './App.css';
import Navbar from './Navbar';

function Dashboard({ user, onLogout }) {
  if (!user) {
    return null; // This won't render since ProtectedRoute handles redirection
  }

  return (
    <div className="dashboard">
      <Navbar user={user} onLogout={onLogout} />
      <div className="dashboard-content">
        <h1>Dashboard</h1>
        <p>Welcome to your dashboard, {user.username}!</p>
        <p>Email: {user.email}</p>
        <img
          src={user.picture || '/icons8-no-picture-48.png'}
          alt="Profile"
          className="dashboard-profile-pic"
        />
      </div>
    </div>
  );
}

export default Dashboard;