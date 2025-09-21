import { reactive } from "vue";

export const authState = reactive({
  isLoggedIn: !!localStorage.getItem("user_id"),
  isAdmin: localStorage.getItem("is_admin") === "true",

  login(user_id, is_admin) {
    localStorage.setItem("user_id", user_id);
    localStorage.setItem("is_admin", is_admin);
    this.isLoggedIn = true;
    this.isAdmin = is_admin === true || is_admin === "true";
  },

  logout() {
    localStorage.removeItem("user_id");
    localStorage.removeItem("is_admin");
    this.isLoggedIn = false;
    this.isAdmin = false;
  },
});
