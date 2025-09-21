<template>
  <div class="container mt-5">
    <h2>Register</h2>
    <form @submit.prevent="register">
      <div class="mb-3">
        <label for="email" class="form-label">Email</label>
        <input
          type="email"
          class="form-control"
          id="email"
          v-model="email"
          required
        />
      </div>
      <div class="mb-3">
        <label for="password" class="form-label">Password</label>
        <input
          type="password"
          class="form-control"
          id="password"
          v-model="password"
          required
        />
      </div>
      <button type="submit" class="btn btn-primary">Register</button>
      <p class="text-danger mt-2" v-if="error">{{ error }}</p>
      <p class="text-success mt-2" v-if="success">{{ success }}</p>
    </form>
  </div>
</template>

<script>
export default {
  name: "RegisterView",
  data() {
    return {
      email: "",
      password: "",
      error: "",
      success: "",
    };
  },
  methods: {
    async register() {
      this.error = "";
      this.success = "";

      try {
        const res = await fetch("/register", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: this.email,
            password: this.password,
          }),
        });

        const data = await res.json();

        if (!res.ok) {
          this.error = data.error || "Registration failed";
        } else {
          this.success = "Registration successful! Please login.";
          this.email = "";
          this.password = "";
        }
      } catch (err) {
        this.error = "Server error. Please try again later.";
      }
    },
  },
};
</script>
