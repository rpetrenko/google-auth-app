import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { act } from 'react'; // Added
import { MemoryRouter } from 'react-router-dom';
import Register from '../Register';

global.fetch = jest.fn();

describe('Register', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('submits registration and shows success message', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: 'Check your email for a verification link.' }),
    });

    await act(async () => {
      render(
        <MemoryRouter>
          <Register />
        </MemoryRouter>
      );
    });

    fireEvent.change(screen.getByPlaceholderText('Username'), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByPlaceholderText('Email'), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'password123' } });
    fireEvent.click(screen.getByRole('button', { name: 'Sign Up' }));

    await waitFor(() => {
      expect(screen.getByText('Check your email for a verification link. Redirecting to login...')).toBeInTheDocument();
    });
  });

  test('shows error for existing email', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Email already registered' }),
    });

    await act(async () => {
      render(
        <MemoryRouter>
          <Register />
        </MemoryRouter>
      );
    });

    fireEvent.change(screen.getByPlaceholderText('Username'), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByPlaceholderText('Email'), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'password123' } });
    fireEvent.click(screen.getByRole('button', { name: 'Sign Up' }));

    await waitFor(() => {
      expect(screen.getByText('Email already registered')).toBeInTheDocument();
    });
  });
});