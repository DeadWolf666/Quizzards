<template>
  <div class="container mt-4">
    <h2 class="mb-3">Manage Quizzes</h2>

    <SearchBar v-model="searchTerm" placeholder="Search quizzes..." />

    <div class="card mb-4 p-3">
      <h5>Add New Quiz</h5>
      <div class="row g-2">
        <div class="col-md-4">
          <label>Subject</label>
          <select
            class="form-select"
            v-model="newQuiz.subjectId"
            @change="fetchChapters"
          >
            <option disabled value="">Select subject</option>
            <option
              v-for="subject in subjects"
              :key="subject.id"
              :value="subject.id"
            >
              {{ subject.name }}
            </option>
          </select>
        </div>

        <div class="col-md-4">
          <label>Chapter</label>
          <select class="form-select" v-model="newQuiz.chapterId">
            <option disabled value="">Select chapter</option>
            <option
              v-for="chapter in filteredChapters"
              :key="chapter.id"
              :value="chapter.id"
            >
              {{ chapter.name }}
            </option>
          </select>
        </div>

        <div class="col-md-4">
          <label>Name</label>
          <input
            class="form-control"
            v-model="newQuiz.name"
            placeholder="Quiz name"
          />
        </div>

        <div class="col-md-4">
          <label>Date</label>
          <input class="form-control" type="date" v-model="newQuiz.date" />
        </div>

        <div class="col-md-4">
          <label>Time</label>
          <input class="form-control" type="time" v-model="newQuiz.time" />
        </div>

        <div class="col-md-4">
          <label>Duration (minutes)</label>
          <input
            class="form-control"
            type="number"
            v-model.number="newQuiz.duration"
          />
        </div>
      </div>

      <button class="btn btn-primary mt-3" @click="createQuiz">Add Quiz</button>
    </div>

    <div class="mb-3">
      <button class="btn btn-danger" @click="toggleDeleteMode">
        {{ deleteMode ? "Cancel" : "Delete Quizzes" }}
      </button>
      <button
        v-if="deleteMode && selectedToDelete.length"
        class="btn btn-warning ms-2"
        @click="confirmDelete"
      >
        Confirm Delete
      </button>
    </div>

    <div class="row">
      <div class="col-md-6 mb-3" v-for="quiz in filteredQuizzes" :key="quiz.id">
        <div class="card p-3">
          <div class="d-flex justify-content-between align-items-center">
            <div v-if="editingQuizId === quiz.id">
              <input class="form-control" v-model="editedQuiz.name" />
            </div>
            <h5 v-else class="mb-0">{{ quiz.name }}</h5>

            <div>
              <button
                v-if="editingQuizId !== quiz.id"
                class="btn btn-sm btn-outline-primary me-2"
                @click="startEdit(quiz)"
              >
                Edit
              </button>
              <button
                v-if="editingQuizId === quiz.id"
                class="btn btn-sm btn-success me-1"
                @click="saveQuiz(quiz.id)"
              >
                Save
              </button>
              <button
                v-if="editingQuizId === quiz.id"
                class="btn btn-sm btn-secondary"
                @click="cancelEdit"
              >
                Cancel
              </button>
              <input
                v-if="deleteMode"
                type="checkbox"
                v-model="selectedToDelete"
                :value="quiz.id"
                class="ms-2"
              />
            </div>
          </div>

          <button
            class="btn btn-link p-0 mt-2"
            @click="quiz.showDetails = !quiz.showDetails"
          >
            {{ quiz.showDetails ? "Hide" : "Show" }} Details
          </button>

          <div v-if="quiz.showDetails" class="mt-2">
            <div v-if="editingQuizId === quiz.id">
              <p>
                <strong>Subject:</strong>
                <select
                  class="form-select"
                  v-model="editedQuiz.subject_id"
                  @change="filterEditedChapters"
                >
                  <option disabled value="">Select subject</option>
                  <option
                    v-for="subj in subjects"
                    :key="subj.id"
                    :value="subj.id"
                  >
                    {{ subj.name }}
                  </option>
                </select>
              </p>
              <p>
                <strong>Chapter:</strong>
                <select class="form-select" v-model="editedQuiz.chapter_id">
                  <option disabled value="">Select chapter</option>
                  <option
                    v-for="chap in editedChapters"
                    :key="chap.id"
                    :value="chap.id"
                  >
                    {{ chap.name }}
                  </option>
                </select>
              </p>
              <p>
                <strong>Date:</strong>
                <input
                  class="form-control"
                  type="date"
                  v-model="editedQuiz.date_of_quiz"
                />
              </p>
              <p>
                <strong>Time:</strong>
                <input
                  class="form-control"
                  type="time"
                  v-model="editedQuiz.time_of_quiz"
                />
              </p>
              <p>
                <strong>Duration (minutes):</strong>
                <input
                  class="form-control"
                  type="number"
                  v-model.number="editedQuiz.duration_minutes"
                />
              </p>
            </div>
            <div v-else>
              <p><strong>Subject:</strong> {{ quiz.subject }}</p>
              <p><strong>Chapter:</strong> {{ quiz.chapter }}</p>
              <p><strong>Date:</strong> {{ quiz.date || "N/A" }}</p>
              <p><strong>Time:</strong> {{ quiz.time || "N/A" }}</p>
              <p>
                <strong>Duration:</strong>
                {{ formatDuration(quiz.duration) }}
              </p>
            </div>
            <button
              class="btn btn-outline-info mt-2"
              @click="quiz.showQuestions = !quiz.showQuestions"
            >
              {{ quiz.showQuestions ? "Hide Questions" : "Questions" }}
            </button>
            <QuestionManager
              v-if="quiz.showQuestions"
              :quiz-id="quiz.id"
              class="mt-3"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import QuestionManager from "./QuestionManager.vue";
import SearchBar from "./SearchBar.vue";

export default {
  components: {
    QuestionManager,
    SearchBar,
  },
  data() {
    return {
      quizzes: [],
      subjects: [],
      chapters: [],
      deleteMode: false,
      selectedToDelete: [],
      searchTerm: "",
      newQuiz: {
        subjectId: "",
        chapterId: "",
        name: "",
        date: "",
        time: "",
        duration: 0,
      },
      editingQuizId: null,
      editedQuiz: {},
      editedChapters: [],
    };
  },
  computed: {
    filteredChapters() {
      return this.chapters.filter(
        (ch) => ch.subject_id === this.newQuiz.subjectId
      );
    },
    filteredQuizzes() {
      const term = this.searchTerm.trim().toLowerCase();
      if (!term) return this.quizzes;

      return this.quizzes.filter((quiz) => {
        const nameMatch = quiz.name?.toLowerCase().includes(term);
        const subjectMatch = quiz.subject?.toLowerCase().includes(term);
        const chapterMatch = quiz.chapter?.toLowerCase().includes(term);

        // Match question text (questions assumed to be pre-fetched inside quiz object)
        const questionMatch = Array.isArray(quiz.questions)
          ? quiz.questions.some((q) => q.text.toLowerCase().includes(term))
          : false;

        return nameMatch || subjectMatch || chapterMatch || questionMatch;
      });
    },
  },
  methods: {
    async fetchQuizzes() {
      const res = await fetch("/admin/quizzes");
      if (res.ok) {
        const data = await res.json();
        this.quizzes = data.map((q) => ({
          ...q,
          questions: q.questions || [], // ensure questions array exists
          showDetails: false,
          showQuestions: false,
        }));
      } else {
        this.quizzes = [];
      }
    },
    async fetchSubjects() {
      const res = await fetch("/admin/subjects");
      this.subjects = await res.json();
    },
    async fetchChapters() {
      const res = await fetch("/admin/chapters");
      const data = await res.json();
      this.chapters = data.chapters || [];
    },
    formatDuration(seconds) {
      const hrs = String(Math.floor(seconds / 3600)).padStart(2, "0");
      const mins = String(Math.floor((seconds % 3600) / 60)).padStart(2, "0");
      const secs = String(seconds % 60).padStart(2, "0");
      return `${hrs}:${mins}:${secs}`;
    },
    async createQuiz() {
      const body = {
        chapter_id: this.newQuiz.chapterId,
        name: this.newQuiz.name,
        date: this.newQuiz.date,
        time: this.newQuiz.time,
        duration: this.newQuiz.duration * 60,
      };
      const res = await fetch("/admin/quizzes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (res.ok) {
        this.newQuiz = {
          subjectId: "",
          chapterId: "",
          name: "",
          date: "",
          time: "",
          duration: 0,
        };
        this.fetchQuizzes();
      } else {
        alert("Error creating quiz");
      }
    },
    toggleDeleteMode() {
      this.deleteMode = !this.deleteMode;
      this.selectedToDelete = [];
    },
    async confirmDelete() {
      if (!confirm("Are you sure you want to delete selected quizzes?")) return;
      for (const id of this.selectedToDelete) {
        await fetch(`/admin/quizzes/${id}`, { method: "DELETE" });
      }
      this.toggleDeleteMode();
      this.fetchQuizzes();
    },
    startEdit(quiz) {
      this.editingQuizId = quiz.id;
      this.editedQuiz = {
        name: quiz.name,
        date_of_quiz: quiz.date,
        time_of_quiz: quiz.time,
        duration_minutes: Math.floor(quiz.duration / 60),
        subject_id: this.subjects.find((s) => s.name === quiz.subject)?.id,
        chapter_id: this.chapters.find((c) => c.name === quiz.chapter)?.id,
      };
      this.filterEditedChapters();
    },
    cancelEdit() {
      this.editingQuizId = null;
      this.editedQuiz = {};
    },
    async saveQuiz(quizId) {
      const payload = {
        name: this.editedQuiz.name,
        date_of_quiz: this.editedQuiz.date_of_quiz,
        time_of_quiz: this.editedQuiz.time_of_quiz,
        duration_seconds: Number(this.editedQuiz.duration_minutes * 60),
        chapter_id: this.editedQuiz.chapter_id,
      };
      const res = await fetch(`/admin/quizzes/${quizId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        await this.fetchQuizzes();
        this.cancelEdit();
      } else {
        alert("Failed to update quiz");
      }
    },
    filterEditedChapters() {
      this.editedChapters = this.chapters.filter(
        (ch) => ch.subject_id === this.editedQuiz.subject_id
      );
    },
  },
  mounted() {
    this.fetchSubjects();
    this.fetchChapters();
    this.fetchQuizzes();
  },
};
</script>

<style scoped>
.card:hover {
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  transition: 0.3s ease;
}
</style>
