import { useEffect, useState } from "react";
import { getMe } from "../api";

export default function Dashboard() {
  const [user, setUser] = useState<any>(null);
  const token = localStorage.getItem("token")!;

  useEffect(() => {
    getMe(token).then((res) => setUser(res.data));
  }, [token]);

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Dashboard</h1>
      {user ? <p>Welcome, {user.email}!</p> : <p>Loading…</p>}
      <button onClick={() => { localStorage.removeItem("token"); window.location.href="/login"; }}>
        Logout
      </button>
    </div>
  );
}
