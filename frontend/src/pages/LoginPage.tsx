import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { login, register } from "../api";

export default function LoginPage() {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      if (isRegister) {
        await register(email, password);
        // auto-login after register
        const { data } = await login(email, password);
        localStorage.setItem("token", data.access_token);
      } else {
        const { data } = await login(email, password);
        localStorage.setItem("token", data.access_token);
      }
      navigate("/");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Something went wrong");
    }
  };

  return (
    <div style={styles.container}>
      <h2>{isRegister ? "Create Account" : "Login"}</h2>
      <form onSubmit={submit} style={styles.form}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          style={styles.input}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={styles.input}
        />
        {error && <p style={{ color: "red" }}>{error}</p>}
        <button type="submit" style={styles.btn}>
          {isRegister ? "Register" : "Login"}
        </button>
      </form>

      <p>
        {isRegister ? "Already have an account?" : "Need an account?"}{" "}
        <a href="#" onClick={() => setIsRegister(!isRegister)}>
          {isRegister ? "Login" : "Register"}
        </a>
      </p>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: { maxWidth: 360, margin: "4rem auto", textAlign: "center" },
  form: { display: "flex", flexDirection: "column", gap: "1rem" },
  input: { padding: "0.8rem", fontSize: "1rem" },
  btn: { padding: "0.8rem", fontSize: "1rem", cursor: "pointer" },
};
