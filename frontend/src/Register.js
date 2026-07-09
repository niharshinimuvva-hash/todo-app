import { useState } from "react";
import axios from "axios";
import "./Auth.css";

function Register({ showLogin }) {

  const [username, setUsername] =
    useState("");

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [confirmPassword, setConfirmPassword] =
    useState("");

  const [error, setError] =
    useState("");

  async function handleRegister(e) {

    e.preventDefault();

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    try {

      await axios.post("/api/register", {
        username,
        email,
        password,
      });

      alert(
        "Registration successful. Please login."
      );

      showLogin();

    } catch {

      setError(
        "Email already exists"
      );

    }
  }

  return (
    <div className="Auth">

      <form
        className="auth-card"
        onSubmit={handleRegister}
      >

        <h2>Create Account</h2>

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) =>
            setUsername(e.target.value)
          }
          required
        />

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

        <input
          type="password"
          placeholder="Confirm Password"
          value={confirmPassword}
          onChange={(e) =>
            setConfirmPassword(e.target.value)
          }
          required
        />

        <button type="submit">
          Register
        </button>

        <p>
          Already have an account?
        </p>

        <button
          type="button"
          className="secondary"
          onClick={showLogin}
        >
          Login
        </button>

      </form>

    </div>
  );
}

export default Register;