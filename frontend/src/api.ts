import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8003", // auth-service
  withCredentials: true, // for httpOnly cookie (optional)
});

export const register = (email: string, password: string) =>
  api.post("/register", { email, password });

export const login = (email: string, password: string) =>
  api.post("/login", { username: email, password });

export const getMe = (token: string) =>
  api.get("/me", {
    headers: { Authorization: `Bearer ${token}` },
  });
