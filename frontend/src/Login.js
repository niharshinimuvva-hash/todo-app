import { useState } from "react";
import axios from "axios";
import "./Auth.css";

function Login({ onLogin, showRegister }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleLogin(e) {
    e.preventDefault();

    try {
      const response = await axios.post("/api/login", {
        email,
        password,
      });

      localStorage.setItem(
        "token",
        response.data.access_token
      );

      axios.defaults.headers.common[
        "Authorization"
      ] = `Bearer ${response.data.access_token}`;

      onLogin();

    } catch (err) {
      setError("Invalid email or password");
    }
  }

  return (
    <div className="Auth">

      <form className="auth-card" onSubmit={handleLogin}>

        <h2>Login</h2>

        {error && (
          <div className="error">{error}</div>
        )}

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) =>
            setEmail(e.target.value)
          }
          required
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) =>
            setPassword(e.target.value)
          }
          required
        />

        <button type="submit">
          Login
        </button>

        <p>
          Don't have an account?
        </p>

        <button
          type="button"
          className="secondary"
          onClick={showRegister}
        >
          Register
        </button>

      </form>

    </div>
  );
}

export default Login;