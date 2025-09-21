<template>
  <div
    v-if="authState.isLoggedIn"
    class="bg-light p-3 border-end"
    style="width: 220px; min-height: 100vh"
  >
    <h5 class="mb-4">Navigation</h5>
    <button
      class="btn btn-outline-primary w-100 mb-2"
      @click="$emit('navigate', 'subjects')"
    >
      Subjects
    </button>
    <button
      class="btn btn-outline-primary w-100 mb-2"
      @click="$emit('navigate', 'quizzes')"
    >
      Quizzes
    </button>
    <button
      class="btn btn-outline-primary w-100 mb-2"
      @click="$emit('navigate', 'users')"
    >
      All Users
    </button>
  </div>
</template>

<script>
import { authState } from "../auth";

export default {
  name: "SideBar",
  setup() {
    return { authState };
  },
};
</script>
