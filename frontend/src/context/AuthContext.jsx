import { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../services/api';

const TOKEN_KEY = 'setux_jwt_token';
const LEGACY_TOKEN_KEY = 'token';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(
    localStorage.getItem(TOKEN_KEY) || localStorage.getItem(LEGACY_TOKEN_KEY) || null
  );
  const [loading, setLoading] = useState(true);

  // Initialize auth state from stored token
  useEffect(() => {
    async function initAuth() {
      const storedToken =
        localStorage.getItem(TOKEN_KEY) || localStorage.getItem(LEGACY_TOKEN_KEY);

      if (storedToken) {
        // Ensure standard key migration
        localStorage.setItem(TOKEN_KEY, storedToken);
        localStorage.removeItem(LEGACY_TOKEN_KEY);

        try {
          const res = await authApi.getMe();
          setUser(res.data);
          setToken(storedToken);
        } catch (err) {
          console.warn("Session validation failed or token expired:", err?.message || err);
          localStorage.removeItem(TOKEN_KEY);
          localStorage.removeItem(LEGACY_TOKEN_KEY);
          setToken(null);
          setUser(null);
        }
      }
      setLoading(false);
    }
    initAuth();
  }, []);

  const login = async (credentials) => {
    const res = await authApi.login(credentials);
    const { access_token, user: userData } = res.data;

    localStorage.setItem(TOKEN_KEY, access_token);
    localStorage.removeItem(LEGACY_TOKEN_KEY);
    setToken(access_token);
    setUser(userData);
    return userData;
  };

  const signup = async (formData) => {
    const res = await authApi.signup(formData);
    const { access_token, user: userData } = res.data;

    localStorage.setItem(TOKEN_KEY, access_token);
    localStorage.removeItem(LEGACY_TOKEN_KEY);
    setToken(access_token);
    setUser(userData);
    return userData;
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (e) {
      // Ignore network errors on logout
    } finally {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(LEGACY_TOKEN_KEY);
      setToken(null);
      setUser(null);
    }
  };

  const value = {
    user,
    token,
    role: user?.role || null,
    isAuthenticated: !!user && !!token,
    loading,
    login,
    signup,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
