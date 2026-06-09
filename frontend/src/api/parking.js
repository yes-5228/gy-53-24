import { http } from "./http";

export const parkingApi = {
  getSpaces: () => http.get("/spaces"),
  updateSpace: (id, payload) => http.patch(`/spaces/${id}`, payload),
  getCards: () => http.get("/monthly-cards"),
  createCard: (payload) => http.post("/monthly-cards", payload),
  updateCard: (id, payload) => http.patch(`/monthly-cards/${id}`, payload),
  getOrders: () => http.get("/parking/orders"),
  entry: (payload) => http.post("/parking/entry", payload),
  calculate: (payload) => http.post("/parking/calculate", payload),
  exit: (id, payload) => http.post(`/parking/exit/${id}`, payload),
  getInvoices: () => http.get("/invoices"),
  createInvoice: (payload) => http.post("/invoices", payload),
};
