<template>
  <div class="mt-3 p-3 border rounded bg-light">
    <h5>Questions for this Quiz</h5>

    <div v-for="q in questions" :key="q.id" class="mb-2 border p-2">
      <div><strong>Q:</strong> {{ q.content }}</div>
      <div>1. {{ q.option1 || "-" }}</div>
      <div>2. {{ q.option2 || "-" }}</div>
      <div>3. {{ q.option3 || "-" }}</div>
      <div>4. {{ q.option4 || "-" }}</div>
      <div><strong>Correct:</strong> {{ q.correct_option }}</div>

      <button class="btn btn-sm btn-warning me-1" @click="editQuestion(q)">
        Edit
      </button>
      <button class="btn btn-sm btn-danger" @click="deleteQuestion(q.id)">
        Delete
      </button>
    </div>

    <div class="mt-3">
      <h6>{{ editingQuestionId ? "Edit Question" : "Add Question" }}</h6>
      <input
        v-model="form.content"
        placeholder="Question"
        class="form-control mb-1"
      />
      <input
        v-model="form.option1"
        placeholder="Option 1"
        class="form-control mb-1"
      />
      <input
        v-model="form.option2"
        placeholder="Option 2"
        class="form-control mb-1"
      />
      <input
        v-model="form.option3"
        placeholder="Option 3"
        class="form-control mb-1"
      />
      <input
        v-model="form.option4"
        placeholder="Option 4"
        class="form-control mb-1"
      />
      <input
        v-model="form.correct_option"
        placeholder="Correct Option"
        class="form-control mb-1"
      />

      <button class="btn btn-success" @click="submitQuestion">
        {{ editingQuestionId ? "Update" : "Add" }}
      </button>
      <button
        v-if="editingQuestionId"
        class="btn btn-secondary ms-2"
        @click="resetForm"
      >
        Cancel
      </button>
    </div>
  </div>
</template>

<script>
export default {
  props: ["quizId"],
  data() {
    return {
      questions: [],
      editingQuestionId: null,
      form: {
        content: "",
        option1: "",
        option2: "",
        option3: "",
        option4: "",
        correct_option: "",
      },
    };
  },
  mounted() {
    this.fetchQuestions();
  },
  methods: {
    fetchQuestions() {
      fetch(`/admin/quizzes/${this.quizId}/questions`, {
        headers: { "Content-Type": "application/json" },
      })
        .then((res) => res.json())
        .then((data) => {
          this.questions = data.questions;
        });
    },
    submitQuestion() {
      const method = this.editingQuestionId ? "PUT" : "POST";
      const url = this.editingQuestionId
        ? `/admin/questions/${this.editingQuestionId}`
        : `/admin/quizzes/${this.quizId}/questions`;

      fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(this.form),
      })
        .then((res) => res.json())
        .then(() => {
          this.fetchQuestions();
          this.resetForm();
        });
    },
    deleteQuestion(id) {
      if (!confirm("Are you sure you want to delete this question?")) return;

      fetch(`/admin/questions/${id}`, { method: "DELETE" }).then(() => {
        this.fetchQuestions();
      });
    },
    editQuestion(question) {
      this.editingQuestionId = question.id;
      this.form = { ...question };
    },
    resetForm() {
      this.editingQuestionId = null;
      this.form = {
        content: "",
        option1: "",
        option2: "",
        option3: "",
        option4: "",
        correct_option: "",
      };
    },
  },
};
</script>

<style scoped>
input {
  width: 100%;
}
</style>
