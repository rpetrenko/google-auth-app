import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Dashboard from '../Dashboard';

describe('Dashboard', () => {
  const user = { username: 'testuser', email: 'test@example.com', picture: 'test.jpg' };
  const onLogout = jest.fn();

  test('renders dashboard with user info', () => {
    render(
      <MemoryRouter>
        <Dashboard user={user} onLogout={onLogout} />
      </MemoryRouter>
    );
    expect(screen.getByRole('heading', { name: 'Dashboard' })).toBeInTheDocument(); // Targets <h1>
    expect(screen.getByText('Welcome to your dashboard, testuser!')).toBeInTheDocument();
    expect(screen.getByText('Email: test@example.com')).toBeInTheDocument();
    expect(screen.getByAltText('Profile')).toHaveAttribute('src', 'test.jpg');
  });
});