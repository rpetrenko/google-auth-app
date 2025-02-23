import '@testing-library/jest-dom';
import { render, screen, fireEvent } from '@testing-library/react';
import App from '../App';

console.log('Starting App.test.js');

describe('App', () => {
  test('renders login page and switches to register', () => {
    console.log('Rendering App');
    const { container } = render(<App />);
    console.log('App rendered, checking DOM:', container.innerHTML);

    console.log('Looking for Login heading');
    expect(screen.getByRole('heading', { name: 'Login' })).toBeInTheDocument();
    console.log('Found Login heading');

    console.log('Looking for Continue with Google');
    expect(screen.getByText('Continue with Google')).toBeInTheDocument();
    console.log('Found Continue with Google');

    console.log('Clicking Sign up');
    fireEvent.click(screen.getByText('Sign up'));
    console.log('Clicked Sign up, checking for Sign Up');

    expect(screen.getByRole('heading', { name: 'Sign Up' })).toBeInTheDocument();
    console.log('Found Sign Up heading');
  });
});