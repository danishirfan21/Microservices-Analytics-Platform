import React, { useState } from 'react';
import axios from 'axios';
import { User, Lock, Mail, UserPlus, LogIn } from 'lucide-react';
import './Login.css';

const USER_SERVICE_URL = process.env.REACT_APP_USER_SERVICE_URL || 'http://localhost:8000';

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await axios.post(`${USER_SERVICE_URL}/login`, {
        username,
        password
      });

      onLogin(response.data.access_token);
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await axios.post(`${USER_SERVICE_URL}/users/`, {
        username,
        email,
        password,
        full_name: fullName
      });

      // Auto-login after registration
      const loginResponse = await axios.post(`${USER_SERVICE_URL}/login`, {
        username,
        password
      });

      onLogin(loginResponse.data.access_token);
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>Analytics Dashboard</h1>
        <h2>{isRegistering ? 'Register' : 'Login'}</h2>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={isRegistering ? handleRegister : handleLogin}>
          {isRegistering && (
            <>
              <div className="form-group">
                <label>Email</label>
                <div className="input-with-icon">
                  <Mail size={18} />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    placeholder="Enter your email"
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Full Name</label>
                <div className="input-with-icon">
                  <User size={18} />
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Enter your full name"
                  />
                </div>
              </div>
            </>
          )}

          <div className="form-group">
            <label>Username</label>
            <div className="input-with-icon">
              <User size={18} />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                placeholder="Enter your username"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Password</label>
            <div className="input-with-icon">
              <Lock size={18} />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="Enter your password"
              />
            </div>
          </div>

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? (
              'Processing...'
            ) : isRegistering ? (
              <>
                <UserPlus size={18} style={{ marginRight: '8px' }} />
                Register
              </>
            ) : (
              <>
                <LogIn size={18} style={{ marginRight: '8px' }} />
                Login
              </>
            )}
          </button>
        </form>

        <p className="toggle-text">
          {isRegistering ? 'Already have an account?' : "Don't have an account?"}
          <button
            className="toggle-btn"
            onClick={() => {
              setIsRegistering(!isRegistering);
              setError('');
            }}
          >
            {isRegistering ? 'Login' : 'Register'}
          </button>
        </p>
      </div>
    </div>
  );
}

export default Login;
