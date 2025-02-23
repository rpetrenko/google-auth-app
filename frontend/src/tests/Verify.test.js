import '@testing-library/jest-dom';
import { render, screen, waitFor } from '@testing-library/react';
import { act } from 'react';
import { MemoryRouter } from 'react-router-dom';
import Verify from '../Verify';

global.fetch = jest.fn();

describe('Verify', () => {
  test('verifies email successfully', async () => {
    fetch.mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ message: 'Email verified successfully. You can now log in.' }),
      })
    );

    // Render and check initial state
    act(() => {
      render(
        <MemoryRouter initialEntries={['/verify?token=abc123']}>
          <Verify />
        </MemoryRouter>
      );
    });
    expect(screen.getByText('Verifying your email...')).toBeInTheDocument();

    // Wait for async update
    await waitFor(() => {
      expect(screen.getByText('Email verified successfully! Redirecting to login...')).toBeInTheDocument();
    });
  });
});