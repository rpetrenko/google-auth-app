import '@testing-library/jest-dom'; // Added for toBeInTheDocument
import { render, screen, waitFor } from '@testing-library/react'; // Fixed typo
import { MemoryRouter } from 'react-router-dom';
import Verify from '../Verify';

global.fetch = jest.fn();

describe('Verify', () => {
  test('verifies email successfully', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: 'Email verified successfully. You can now log in.' }),
    });

    render(
      <MemoryRouter initialEntries={['/verify?token=abc123']}>
        <Verify />
      </MemoryRouter>
    );

    expect(screen.getByText('Verifying your email...')).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText('Email verified successfully! Redirecting to login...')).toBeInTheDocument();
    });
  });
});