<template>
  <div>
    <h3>All Registered Users</h3>
    <SearchBar
      v-model="searchTerm"
      placeholder="Search by email, quiz or question..."
    />
    <button class="btn btn-primary mb-3" @click="exportAllUsersData">
      Export All Users' Performance CSV
    </button>

    <div v-for="user in filteredUsers" :key="user.id" class="card my-3">
      <div
        class="card-header d-flex justify-content-between align-items-center"
      >
        <strong>{{ user.email }}</strong>
        <button
          class="btn btn-sm btn-outline-primary"
          @click="toggleUser(user.id)"
        >
          {{ expandedUser === user.id ? "Hide Quizzes" : "Show Quizzes" }}
        </button>
      </div>

      <div v-if="expandedUser === user.id" class="card-body">
        <p v-if="!user.quizzes.length" class="text-muted">
          No quizzes attempted.
        </p>

        <div v-for="quiz in user.quizzes" :key="quiz.id" class="mb-3">
          <div class="d-flex justify-content-between">
            <div>
              <strong>{{ quiz.name }}</strong> - {{ quiz.date || "No date" }} -
              <em>Score: {{ quiz.score }}</em>
            </div>
            <button
              class="btn btn-sm btn-outline-secondary"
              @click="toggleQuiz(quiz.score_id)"
            >
              {{
                expandedQuiz === quiz.score_id ? "Hide Details" : "Show Details"
              }}
            </button>
          </div>

          <div v-if="expandedQuiz === quiz.score_id" class="mt-2">
            <ul class="list-group">
              <li
                v-for="detail in quiz.details"
                :key="detail.question"
                class="list-group-item"
              >
                <p><strong>Q:</strong> {{ detail.question }}</p>
                <p><strong>User Answer:</strong> {{ detail.user_answer }}</p>
                <p>
                  <strong>Correct Answer:</strong> {{ detail.correct_answer }}
                </p>
                <small
                  ><em>Options: {{ detail.options.join(", ") }}</em></small
                >
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SearchBar from "./SearchBar.vue";

export default {
  name: "UserManager",
  components: { SearchBar },
  data() {
    return {
      users: [],
      searchTerm: "",
      expandedUser: null,
      expandedQuiz: null,
    };
  },
  computed: {
    filteredUsers() {
      const term = this.searchTerm.toLowerCase().trim();
      if (!term) return this.users;

      return this.users.filter((user) => {
        const emailMatch = user.email.toLowerCase().includes(term);

        const quizMatch = user.quizzes.some((q) =>
          q.name.toLowerCase().includes(term)
        );

        const questionMatch = user.quizzes.some((q) =>
          q.details.some((d) => d.question.toLowerCase().includes(term))
        );

        return emailMatch || quizMatch || questionMatch;
      });
    },
  },
  methods: {
    async fetchUsers() {
      const res = await fetch("/admin/users");
      const data = await res.json();
      this.users = data;
    },
    toggleUser(userId) {
      this.expandedUser = this.expandedUser === userId ? null : userId;
    },
    toggleQuiz(scoreId) {
      this.expandedQuiz = this.expandedQuiz === scoreId ? null : scoreId;
    },
    async exportAllUsersData() {
      try {
        const res = await fetch("/admin/export-all-users", {
          method: "POST",
          credentials: "include",
        });
        if (!res.ok) {
          throw new Error("Failed to trigger export");
        }
        alert("Export started. Check the exports folder after some time.");
      } catch (err) {
        console.error(err);
        alert("Something went wrong.");
      }
    },
  },
  mounted() {
    this.fetchUsers();
  },
};
</script>
