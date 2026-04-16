import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';
import '@testing-library/jest-dom';

test('renders login page by default', () => {
  render(<App />);
  const loginElements = screen.getAllByText(/Login/i);
  expect(loginElements.length).toBeGreaterThan(0);
});

test('renders registration toggle', () => {
  render(<App />);
  const registerText = screen.getByText(/Don't have an account\?/i);
  expect(registerText).toBeInTheDocument();
  const registerButton = screen.getByRole('button', { name: /Register/i });
  expect(registerButton).toBeInTheDocument();
});
