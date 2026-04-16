import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from './App';
import '@testing-library/jest-dom';
import axios from 'axios';

jest.mock('axios');

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

test('handles login failure gracefully', async () => {
  axios.post.mockRejectedValueOnce({
    response: {
      data: { detail: 'Invalid credentials' },
      status: 401
    }
  });

  render(<App />);

  const usernameInput = screen.getByPlaceholderText(/Enter your username/i);
  const passwordInput = screen.getByPlaceholderText(/Enter your password/i);
  const loginButton = screen.getByRole('button', { name: /Login/i });

  fireEvent.change(usernameInput, { target: { value: 'wronguser' } });
  fireEvent.change(passwordInput, { target: { value: 'wrongpass' } });
  fireEvent.click(loginButton);

  await waitFor(() => {
    expect(screen.getByText(/Invalid credentials/i)).toBeInTheDocument();
  });
});

test('handles network error during login', async () => {
  axios.post.mockRejectedValueOnce(new Error('Network Error'));

  render(<App />);

  const loginButton = screen.getByRole('button', { name: /Login/i });
  fireEvent.click(loginButton);

  await waitFor(() => {
    expect(screen.getByText(/Login failed. Please try again./i)).toBeInTheDocument();
  });
});
