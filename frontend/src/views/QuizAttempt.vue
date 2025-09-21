<template>
  <div class="container mt-4">
    <h2 class="mb-4">{{ quiz.name }}</h2>

    <div v-if="loading" class="text-center">Loading quiz...</div>

    <div v-else>
      <div v-if="error" class="alert alert-danger">{{ error }}</div>

      <div v-else>
        <div class="d-flex justify-content-between mb-3">
          <h5>Time Remaining: {{ formatTime(timer) }}</h5>
        </div>

        <form @submit.prevent="submitQuiz">
          <div
            v-for="q in quiz.questions"
            :key="q.id"
            class="mb-4 p-3 border rounded"
          >
            <p class="fw-semibold">{{ q.content }}</p>
            <div v-for="(option, idx) in q.options" :key="idx">
              <label class="form-check-label">
                <input
                  type="radio"
                  class="form-check-input me-2"
                  :name="q.id"
                  :value="option"
                  v-model="answers[q.id]"
                />
                {{ option }}
              </label>
            </div>
          </div>

          <button type="submit" class="btn btn-primary w-100">
            Submit Quiz
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "QuizAttempt",
  data() {
    return {
      quiz: {},
      answers: {},
      loading: true,
      error: "",
      timer: 0,
      timerInterval: null,
    };
  },
  methods: {
    async fetchQuiz() {
      try {
        const res = await fetch(`/user/quiz/${this.$route.params.quizId}`);
        if (!res.ok) {
          const errData = await res.json();
          this.error = errData.error || "Unable to load quiz.";
          return;
        }
        const data = await res.json();
        this.quiz = data;
        this.timer = data.duration;
        this.startTimer();
      } catch (err) {
        this.error = "Failed to fetch quiz.";
      } finally {
        this.loading = false;
      }
    },
    startTimer() {
      this.timerInterval = setInterval(() => {
        if (this.timer > 0) {
          this.timer--;
        } else {
          clearInterval(this.timerInterval);
          this.submitQuiz();
        }
      }, 1000);
    },
    async submitQuiz() {
      clearInterval(this.timerInterval);
      try {
        const res = await fetch(
          `/user/quiz/${this.$route.params.quizId}/submit`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ answers: this.answers }),
          }
        );
        const data = await res.json();
        if (!res.ok) {
          this.error = data.error || "Failed to submit quiz.";
          return;
        }
        alert(`Your Score: ${data.score}/${data.total}`);
        this.$router.push("/user");
      } catch (err) {
        this.error = "Error submitting quiz.";
      }
    },
    formatTime(seconds) {
      const m = Math.floor(seconds / 60);
      const s = seconds % 60;
      return `${m.toString().padStart(2, "0")}:${s
        .toString()
        .padStart(2, "0")}`;
    },
  },
  mounted() {
    this.fetchQuiz();
  },
  beforeUnmount() {
    clearInterval(this.timerInterval);
  },
};
</script>
