import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import AdminDashboard from "../views/AdminDashboard.vue";
import UserDashboard from "../views/UserDashboard.vue";
import QuizAttempt from "@/views/QuizAttempt.vue";

const routes = [
  { path: "/", name: "Home", component: HomeView },
  { path: "/login", name: "Login", component: LoginView },
  { path: "/register", name: "Register", component: RegisterView },
  {
    path: "/admin",
    name: "AdminDashboard",
    component: AdminDashboard,
    meta: { requiresAdmin: true },
  },
  {
    path: "/user",
    name: "UserDashboard",
    component: UserDashboard,
    meta: { requiresAuth: true },
  },
  {
    path: "/quiz/:quizId",
    name: "QuizAttempt",
    component: QuizAttempt,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const isAdmin = localStorage.getItem("is_admin") === "true";
  const isLoggedIn = !!localStorage.getItem("user_id");

  if (to.meta.requiresAdmin) {
    if (isLoggedIn && isAdmin) {
      next();
    } else {
      next("/login");
    }
  } else if (to.meta.requiresAuth) {
    if (isLoggedIn) {
      next();
    } else {
      next("/login");
    }
  } else {
    next();
  }
});

export default router;
