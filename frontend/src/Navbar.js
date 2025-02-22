import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './App.css';

function Navbar({ user, onLogout }) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const menuRef = useRef(null);

  const toggleDropdown = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };

  const handleClickOutside = (event) => {
    if (menuRef.current && !menuRef.current.contains(event.target)) {
      setIsDropdownOpen(false);
    }
  };

  useEffect(() => {
    // Add event listener when dropdown is open
    if (isDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    // Cleanup listener when dropdown closes or component unmounts
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isDropdownOpen]); // Re-run effect when isDropdownOpen changes

  // Use cached image if available
  const cachedImage = localStorage.getItem(`profile_picture_${user.email}`);
  const profileImage = cachedImage || user.picture || '/icons8-no-picture-48.png';

  const handleImageError = (e) => {
    console.error('Profile picture failed to load:', user.picture);
    e.target.src = '/icons8-no-picture-48.png';
  };

  return (
    <nav className="navbar">
      <div className="navbar-left">
        <Link to="/dashboard" className="navbar-brand">Dashboard</Link>
      </div>
      <div className="navbar-right">
        {user && (
          <div className="user-menu" ref={menuRef}>
            <button className="user-menu-button" onClick={toggleDropdown}>
              <img
                src={profileImage}
                alt="User"
                className="user-picture"
                onError={handleImageError}
                onLoad={(e) => {
                  if (!cachedImage && user.picture) {
                    localStorage.setItem(`profile_picture_${user.email}`, user.picture);
                  }
                }}
              />
              <span className="username">{user.username}</span>
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