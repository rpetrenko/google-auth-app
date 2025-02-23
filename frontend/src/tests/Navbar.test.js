import '@testing-library/jest-dom';
import { render, screen, fireEvent } from '@testing-library/react';
import { act } from 'react';
import { MemoryRouter } from 'react-router-dom';
import Navbar from '../Navbar';

describe('Navbar', () => {
  const user = { username: 'testuser', email: 'test@example.com', picture: 'test.jpg' };
  const onLogout = jest.fn();

  test('renders user info and dropdown', () => {
    act(() => {
      render(
        <MemoryRouter>
          <Navbar user={user} onLogout={onLogout} />
        </MemoryRouter>
      );
    });
    expect(screen.getByText('testuser')).toBeInTheDocument();
    expect(screen.getByAltText('User')).toHaveAttribute('src', 'test.jpg');

    fireEvent.click(screen.getByText('testuser'));
    expect(screen.getByText('Profile')).toBeInTheDocument();
    expect(screen.getByText('Logout')).toBeInTheDocument();

    fireEvent.click(screen.getByText('Logout'));
    expect(onLogout).toHaveBeenCalled();
  });
});