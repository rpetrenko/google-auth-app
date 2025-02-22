import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './App.css';

function Navbar({ user, onLogout }) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const toggleDropdown = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };

  return (
    <nav className="navbar">
      <div className="navbar-left">
        <Link to="/dashboard" className="navbar-brand">Dashboard</Link>
      </div>
      <div className="navbar-right">
        {user && (
          <div className="user-menu">
            <button className="user-menu-button" onClick={toggleDropdown}>
              <img
                src={user.picture || 'https://via.placeholder.com/30'}
                alt="User"
                className="user-picture"
              />
              <span className="username">{user.username} ...</span>
            </button>
            {isDropdownOpen && (
              <div className="dropdown">
                <Link to="/dashboard" className="dropdown-item" onClick={() => setIsDropdownOpen(false)}>
                  Profile
                </Link>
                <button
                  onClick={() => {
                    onLogout();
                    setIsDropdownOpen(false);
                  }}
                  className="dropdown-item logout-button"
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}

export default Navbar;