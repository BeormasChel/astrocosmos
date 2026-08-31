import axios from "axios";

/** HTTP-клиент к ядру `/api/v1`. */
export const apiClient = axios.create({
  baseURL: "/api/v1",
  timeout: 10_000,
});
