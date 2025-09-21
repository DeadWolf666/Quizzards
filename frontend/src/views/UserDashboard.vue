<template>
  <div class="container mt-4">
    <h2 class="mb-4">Available Quizzes</h2>

    <SearchBar
      v-model="searchQuery"
      placeholder="Search by subject, chapter or quiz name..."
    />
    <!-- <button class="btn btn-primary mb-3" @click="exportUserHistory">
      Export Your History CSV
    </button> -->

    <div v-if="loading" class="text-center mt-3">Loading quizzes...</div>

    <div v-else>
      <div v-for="subject in filteredSubjects" :key="subject.id" class="mb-5">
        <div class="card shadow-sm">
          <div class="card-body">
            <h4 class="card-title text-primary">{{ subject.name }}</h4>

            <div
              v-for="chapter in subject.chapters"
              :key="chapter.id"
              class="ms-3 mt-3"
            >
              <h6 class="text-secondary">{{ chapter.name }}</h6>

              <ul v-if="chapter.quizzes.length > 0" class="list-unstyled ms-3">
                <li v-for="quiz in chapter.quizzes" :key="quiz.id" class="mb-2">
                  <a
                    href="#"
                    @click.prevent="goToQuiz(quiz.id)"
                    class="fw-semibold text-decoration-none"
                  >
                    {{ quiz.name }}
                  </a>
                  <small class="text-muted ms-2">
                    (Date:
                    {{ formatQuizDateTime(quiz) }}, Duration:
                    {{ formatDuration(quiz.duration) }})
                  </small>
                </li>
              </ul>

              <p v-else class="text-muted ms-3">No quizzes yet.</p>
            </div>
          </div>
        </div>
      </div>

      <div class="mt-5">
        <button
          class="btn btn-outline-primary w-100"
          type="button"
          @click="togglePastAttempts"
        >
          {{ showPastAttempts ? "Hide" : "View" }} Past Attempts
        </button>

        <div v-show="showPastAttempts" class="mt-3">
          <div v-if="loadingPastAttempts" class="text-center">
            Loading past attempts...
          </div>
          <div v-else>
            <div v-if="pastAttempts.length > 0" class="card shadow-sm">
              <div class="card-body">
                <h5 class="card-title mb-3">Your Previous Quiz Attempts</h5>
                <table class="table table-striped">
                  <thead>
                    <tr>
                      <th>Quiz</th>
                      <th>Date Attempted</th>
                      <th>Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    <template v-for="attempt in pastAttempts" :key="attempt.id">
                      <tr
                        @click="toggleDetails(attempt.id)"
                        style="cursor: pointer"
                      >
                        <td>{{ attempt.quiz_name }}</td>
                        <td>
                          {{ formatDateTime(attempt.time_stamp_of_attempt) }}
                        </td>
                        <td>{{ attempt.total_scored }}</td>
                      </tr>
                      <tr v-if="expandedAttempt === attempt.id">
                        <td colspan="3">
                          <div v-if="loadingDetails">Loading...</div>
                          <div v-else>
                            <ul>
                              <li v-for="q in attemptDetails" :key="q.question">
                                <strong>{{ q.question }}</strong>
                                <ul>
                                  <li
                                    v-for="(opt, i) in q.options"
                                    :key="i"
                                    :style="{
                                      color:
                                        opt === q.correct_answer
                                          ? 'green'
                                          : opt === q.user_answer
                                          ? 'red'
                                          : 'black',
                                    }"
                                  >
                                    {{ opt }}
                                  </li>
                                </ul>
                              </li>
                            </ul>
                          </div>
                        </td>
                      </tr>
                    </template>
                  </tbody>
                </table>
              </div>
            </div>
            <p v-else class="text-muted text-center">
              You have no past quiz attempts.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SearchBar from "../components/SearchBar.vue";

export default {
  name: "UserDashboard",
  components: { SearchBar },
  data() {
    return {
      subjects: [],
      searchQuery: "",
      loading: true,
      pastAttempts: [],
      loadingPastAttempts: false,
      showPastAttempts: false,
      expandedAttempt: null,
      attemptDetails: [],
      loadingDetails: false,
    };
  },
  computed: {
    filteredSubjects() {
      if (!this.searchQuery.trim()) return this.subjects;

      const q = this.searchQuery.toLowerCase();

      return this.subjects
        .map((subject) => {
          const subjectMatches = subject.name.toLowerCase().includes(q);

          const filteredChapters = subject.chapters
            .map((chapter) => {
              const chapterMatches = chapter.name.toLowerCase().includes(q);

              const filteredQuizzes = chapter.quizzes.filter((quiz) =>
                quiz.name.toLowerCase().includes(q)
              );

              if (chapterMatches || filteredQuizzes.length > 0) {
                return {
                  ...chapter,
                  quizzes: chapterMatches ? chapter.quizzes : filteredQuizzes,
                };
              }
              return null;
            })
            .filter((ch) => ch !== null);

          if (subjectMatches || filteredChapters.length > 0) {
            return { ...subject, chapters: filteredChapters };
          }
          return null;
        })
        .filter((s) => s !== null);
    },
  },
  methods: {
    async fetchSubjects() {
      try {
        const res = await fetch("/user/subjects");
        const data = await res.json();
        this.subjects = data.subjects || [];
      } catch (err) {
        console.error("Error fetching subjects:", err);
      } finally {
        this.loading = false;
      }
    },
    async togglePastAttempts() {
      this.showPastAttempts = !this.showPastAttempts;
      if (this.showPastAttempts && this.pastAttempts.length === 0) {
        this.loadingPastAttempts = true;
        try {
          const res = await fetch("/user/scores");
          const data = await res.json();
          this.pastAttempts = data.scores || [];
        } catch (err) {
          console.error("Error fetching past attempts:", err);
        } finally {
          this.loadingPastAttempts = false;
        }
      }
    },
    async toggleDetails(scoreId) {
      if (this.expandedAttempt === scoreId) {
        this.expandedAttempt = null;
        return;
      }
      this.expandedAttempt = scoreId;
      this.loadingDetails = true;
      try {
        const res = await fetch(`/user/scores/${scoreId}/details`);
        const data = await res.json();
        this.attemptDetails = data.details || [];
      } catch (err) {
        console.error("Error fetching details:", err);
      } finally {
        this.loadingDetails = false;
      }
    },
    goToQuiz(quizId) {
      this.$router.push({ name: "QuizAttempt", params: { quizId } });
    },
    formatQuizDateTime(quiz) {
      return this.formatDate(quiz.date, quiz.time);
    },
    formatDate(dateStr, timeStr) {
      try {
        const [year, month, day] = dateStr.split("-");
        const [hour, minute] = timeStr.split(":");
        return `${day}/${month}/${year}, ${hour}:${minute}`;
      } catch {
        return `${dateStr} ${timeStr}`;
      }
    },
    formatDateTime(dateTimeStr) {
      const date = new Date(dateTimeStr);
      return date.toLocaleDateString() + " " + date.toLocaleTimeString();
    },
    formatDuration(seconds) {
      const hrs = Math.floor(seconds / 3600);
      const mins = Math.floor((seconds % 3600) / 60);
      const secs = seconds % 60;
      return `${hrs.toString().padStart(2, "0")}:${mins
        .toString()
        .padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
    },
    // async exportUserHistory() {
    //   try {
    //     const res = await fetch("/user/export-history", {
    //       method: "POST",
    //       credentials: "include",
    //     });
    //     if (!res.ok) {
    //       throw new Error("Failed to trigger export");
    //     }
    //     alert("Export started. Check the exports folder after some time.");
    //   } catch (err) {
    //     console.error(err);
    //     alert("Something went wrong.");
    //   }
    // },
  },
  mounted() {
    this.fetchSubjects();
  },
};
</script>

<style scoped>
.card {
  border-left: 5px solid #0d6efd;
  border-radius: 0.5rem;
}
</style>
