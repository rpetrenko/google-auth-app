// frontend/src/setupTests.js
import '@testing-library/jest-dom';

// Suppress React Router future flag warnings
beforeAll(() => {
  jest.spyOn(console, 'warn').mockImplementation((msg) => {
    if (msg.includes('React Router Future Flag Warning')) {
      return; // Swallow the warning
    }
    console.warn(msg); // Let other warnings through
  });
});

afterAll(() => {
  jest.restoreAllMocks(); // Clean up
});