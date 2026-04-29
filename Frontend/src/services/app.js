import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000",
});

export const uploadFile = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return API.post("/upload", formData);
};

export const sendChat = (message) => {
  return API.post("/chat", { message });
};

export const getDataset = (page = 1, pageSize = 10) => {
  return API.get(`/dataset?page=${page}&page_size=${pageSize}`);
};
