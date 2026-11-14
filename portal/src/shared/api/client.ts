import axios from "axios";
import { toApiError } from "./errors";

const API_URL = (
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
).replace(/\/+$/, "");
const BASE_URL = API_URL.endsWith("/api") ? API_URL : `${API_URL}/api`;

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10_000,
  headers: { Accept: "application/json" },
});

// Every failed request becomes an ApiError, so components never see raw Axios errors.
api.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(toApiError(error)),
);
