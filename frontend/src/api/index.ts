import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:5173/api",
  headers: {
    "Content-Type": "application/json",
  },
});

export const fetchUsers = async (username: string, limit: number, offset: number) => {
  const response = await api.get(`/users?username=${username}&limit=${limit}&offset=${offset}`);
  return response.data;
};

export const fetchUserById = async (id: string) => {
  const response = await api.get(`/users/${id}`);
  return response.data;
};

export const fetchUserDuels = async (id: string, limit: number, offset: number) => {
  const response = await api.get(`/users/${id}/duels?limit=${limit}&offset=${offset}`);
  return response.data;
};

export const fetchRankingGraphData = async (id: string) => {
  const response = await api.get(`/users/${id}/ranking`);
  return response.data;
}

export default api;