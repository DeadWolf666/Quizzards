<template>
  <div class="container mt-5" style="max-width: 400px">
    <h2 class="mb-4">Login</h2>
    <form @submit.prevent="handleLogin">
      <div class="mb-3">
        <label>Email</label>
        <input v-model="email" type="email" class="form-control" required />
      </div>
      <div class="mb-3">
        <label>Password</label>
        <input
          v-model="password"
          type="password"
          class="form-control"
          required
        />
      </div>
      <button type="submit" class="btn btn-success w-100">Login</button>
    </form>
    <div v-if="error" class="alert alert-danger mt-3">{{ error }}</div>
  </div>
</template>

<script>
import { authState } from "../auth";
import router from "../router";

export default {
  name: "LoginView",
  data() {
    return {
      email: "",
      password: "",
      error: "",
    };
  },
  methods: {
    async handleLogin() {
      this.error = "";
      try {
        const res = await fetch("/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: this.email,
            password: this.password,
          }),
          credentials: "include",
        });

        if (res.ok) {
          const data = await res.json();
          authState.login(data.user_id, data.is_admin);
          if (data.is_admin) {
            router.push("/admin");
          } else {
            router.push("/user");
          }
        } else {
          const data = await res.json();
          this.error = data.error || "Login failed.";
        }
      } catch (err) {
        this.error = "Unable to connect to server.";
      }
    },
  },
};
</script>
