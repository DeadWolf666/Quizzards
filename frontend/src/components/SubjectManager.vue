<template>
  <div>
    <h3 class="mb-4">Manage Subjects</h3>

    <SearchBar
      v-model="searchQuery"
      placeholder="Search subjects or chapters..."
    />

    <div class="mb-3 d-flex flex-wrap gap-2 mt-3">
      <button class="btn btn-primary" @click="showAddModal = true">
        Add New Subject
      </button>
      <button class="btn btn-danger" @click="toggleDeleteMode">
        {{ deleteMode ? "Cancel Delete" : "Delete Subjects" }}
      </button>
    </div>

    <div class="row">
      <div
        class="col-md-4 mb-3"
        v-for="subject in filteredSubjects"
        :key="subject.id"
      >
        <div class="card h-100">
          <div class="card-body d-flex flex-column">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <div v-if="editingSubjectId !== subject.id">
                <h5 class="card-title mb-0">{{ subject.name }}</h5>
              </div>
              <div v-else class="flex-grow-1 me-2">
                <input
                  v-model="editedSubjectName"
                  class="form-control form-control-sm"
                  :placeholder="subject.name"
                />
              </div>

              <div>
                <button
                  v-if="editingSubjectId !== subject.id"
                  class="btn btn-sm btn-outline-secondary ms-2"
                  @click="startEditingSubject(subject)"
                >
                  Edit
                </button>

                <template v-else>
                  <button
                    class="btn btn-sm btn-success me-1"
                    @click="saveEditedSubject(subject.id)"
                  >
                    Save
                  </button>
                  <button
                    class="btn btn-sm btn-secondary"
                    @click="cancelEditingSubject"
                  >
                    Cancel
                  </button>
                </template>
              </div>
            </div>

            <button
              class="btn btn-outline-primary btn-sm mb-3 align-self-start"
              @click="toggleChapterManager(subject.id)"
            >
              {{
                showingChaptersFor === subject.id
                  ? "Hide Chapter Manager"
                  : "Update Chapters"
              }}
            </button>

            <div v-if="showingChaptersFor === subject.id" class="mb-2">
              <ChapterManager
                :subjectId="subject.id"
                :key="'chapter-' + subject.id"
                class="mt-2"
                @chapters-updated="fetchSubjects"
              />
              <hr />
            </div>

            <div v-if="deleteMode" class="form-check mt-auto pt-2">
              <input
                class="form-check-input"
                type="checkbox"
                :value="subject.id"
                v-model="subjectsToDelete"
                :id="'delete-' + subject.id"
              />
              <label class="form-check-label" :for="'delete-' + subject.id">
                Mark for Deletion
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="deleteMode && subjectsToDelete.length" class="mt-3">
      <button
        class="btn btn-danger"
        @click="deleteSubjects"
        :disabled="subjectsToDelete.length === 0"
      >
        Confirm Deletion
      </button>
    </div>

    <div v-if="showAddModal" class="modal-backdrop">
      <div class="modal-dialog">
        <div class="modal-content p-3">
          <h5>Add New Subject</h5>
          <input
            v-model="newSubjectName"
            class="form-control my-2"
            placeholder="Subject name"
          />
          <div class="text-end">
            <button class="btn btn-secondary me-2" @click="cancelAddModal">
              Cancel
            </button>
            <button class="btn btn-success" @click="addSubject">Add</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ChapterManager from "./ChapterManager.vue";
import SearchBar from "./SearchBar.vue";

export default {
  name: "SubjectManager",
  components: { ChapterManager, SearchBar },
  data() {
    return {
      subjects: [],
      showAddModal: false,
      newSubjectName: "",
      deleteMode: false,
      subjectsToDelete: [],
      showingChaptersFor: null,
      editingSubjectId: null,
      editedSubjectName: "",
      searchQuery: "",
    };
  },
  computed: {
    filteredSubjects() {
      if (!this.searchQuery.trim()) return this.subjects;

      const query = this.searchQuery.toLowerCase();

      return this.subjects.filter((subject) => {
        const subjectMatch = subject.name.toLowerCase().includes(query);

        const chapterMatch =
          subject.chapters &&
          subject.chapters.some((ch) => ch.name.toLowerCase().includes(query));

        return subjectMatch || chapterMatch;
      });
    },
  },
  methods: {
    async fetchSubjects() {
      try {
        const subjectRes = await fetch("/admin/subjects", {
          credentials: "include",
        });
        if (!subjectRes.ok) throw new Error("Unauthorized");
        const subjects = await subjectRes.json();

        const chapterRes = await fetch("/admin/chapters", {
          credentials: "include",
        });
        const chapterData = await chapterRes.json();
        const chapters = chapterData.chapters || [];

        this.subjects = subjects.map((subject) => {
          const subjectChapters = chapters.filter(
            (ch) => ch.subject_id === subject.id
          );
          return { ...subject, chapters: subjectChapters };
        });
      } catch (err) {
        console.error("Error fetching subjects:", err);
        alert("You are not authorized. Please log in as admin.");
      }
    },
    addSubject() {
      if (!this.newSubjectName.trim()) {
        alert("Subject name cannot be empty.");
        return;
      }

      fetch("/admin/subjects", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name: this.newSubjectName }),
        credentials: "include",
      })
        .then((res) => {
          if (!res.ok) throw new Error("Failed to add subject.");
          return res.json();
        })
        .then(() => {
          this.newSubjectName = "";
          this.showAddModal = false;
          this.fetchSubjects();
        })
        .catch((err) => {
          console.error("Error adding subject:", err);
          alert("Failed to add subject. Please check permissions.");
        });
    },
    cancelAddModal() {
      this.newSubjectName = "";
      this.showAddModal = false;
    },
    toggleDeleteMode() {
      this.deleteMode = !this.deleteMode;
      this.subjectsToDelete = [];
    },
    toggleChapterManager(subjectId) {
      this.showingChaptersFor =
        this.showingChaptersFor === subjectId ? null : subjectId;
    },
    deleteSubjects() {
      fetch("/admin/subjects/delete", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ ids: this.subjectsToDelete }),
        credentials: "include",
      })
        .then((res) => {
          if (!res.ok) throw new Error("Failed to delete subjects.");
          return res.json();
        })
        .then(() => {
          this.deleteMode = false;
          this.subjectsToDelete = [];
          this.fetchSubjects();
        })
        .catch((err) => {
          console.error("Error deleting subjects:", err);
          alert("Failed to delete subjects. Please check permissions.");
        });
    },
    startEditingSubject(subject) {
      this.editingSubjectId = subject.id;
      this.editedSubjectName = subject.name;
    },
    cancelEditingSubject() {
      this.editingSubjectId = null;
      this.editedSubjectName = "";
    },
    async saveEditedSubject(subjectId) {
      try {
        const response = await fetch(`/admin/subjects/${subjectId}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: this.editedSubjectName }),
        });

        if (!response.ok) {
          throw new Error("Failed to update subject");
        }

        this.fetchSubjects();
        this.cancelEditingSubject();
      } catch (error) {
        console.error(error);
        alert("Error updating subject.");
      }
    },
  },
  mounted() {
    this.fetchSubjects();
  },
};
</script>

<style scoped>
.card-title:hover {
  text-decoration: underline;
}
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
