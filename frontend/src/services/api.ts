// Couche centralisée d'appels à l'API backend
import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
});

export default api;

// TODO: sendChatMessage(), uploadDocument(), uploadImage(), transcribeAudio()
