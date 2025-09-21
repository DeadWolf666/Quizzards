<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light">
    <div class="container-fluid">
      <router-link class="navbar-brand" to="/">Quizzards</router-link>
      <div class="collapse navbar-collapse">
        <ul class="navbar-nav ms-auto mb-2 mb-lg-0">
          <li class="nav-item" v-if="!auth.isLoggedIn">
            <router-link class="nav-link" to="/login">Login</router-link>
          </li>
          <li class="nav-item" v-if="!auth.isLoggedIn">
            <router-link class="nav-link" to="/register">Register</router-link>
          </li>
          <li class="nav-item" v-if="auth.isAdmin">
            <router-link class="nav-link" to="/admin"
              >Admin Dashboard</router-link
            >
          </li>
          <li class="nav-item" v-if="auth.isLoggedIn && !auth.isAdmin">
            <router-link class="nav-link" to="/user"
              >User Dashboard</router-link
            >
          </li>
          <li class="nav-item" v-if="auth.isLoggedIn">
            <a class="nav-link" href="#" @click.prevent="logout">Logout</a>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import { authState } from "../auth";

export default {
  name: "NavBar",
  setup() {
    return {
      auth: authState,
    };
  },
  methods: {
    async logout() {
      try {
        const res = await fetch("/logout", {
          method: "POST",
          credentials: "include",
        });

        if (!res.ok) {
          console.error("Logout failed:", await res.text());
        }
      } catch (err) {
        console.error("Logout request error", err);
      } finally {
        this.auth.logout();
        this.$router.push("/");
      }
    },
  },
};
</script>
