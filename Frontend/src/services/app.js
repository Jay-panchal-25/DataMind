import axios from "axios";

const SESSION_KEY = "datamind_session_id";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
});

export function getSessionId() {
  return window.sessionStorage.getItem(SESSION_KEY) || "";
}

export function setSessionId(sessionId) {
  if (!sessionId) {
    window.sessionStorage.removeItem(SESSION_KEY);
    return;
  }
  window.sessionStorage.setItem(SESSION_KEY, sessionId);
}

function withSession(headers = {}) {
  const sessionId = getSessionId();
  if (!sessionId) {
    return headers;
  }

  return {
    ...headers,
    "X-Session-ID": sessionId,
  };
}

export const uploadFile = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return API.post("/upload", formData);
};

export const sendChat = (message) => {
  return API.post(
    "/chat",
    { message },
    { headers: withSession() }
  );
};

export const getDataset = (page = 1, pageSize = 10) => {
  return API.get(`/dataset?page=${page}&page_size=${pageSize}`, {
    headers: withSession(),
  });
};
