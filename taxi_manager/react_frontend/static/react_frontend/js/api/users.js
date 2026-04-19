import { fetchDataJSON } from "./fetch-data.js";
const loadUserInfo = async () => {
  return await fetchDataJSON("/api/v1/auth/users/me/");
};
const logout = () => {
  localStorage.removeItem("tokenAuth");
};
export { loadUserInfo, logout };