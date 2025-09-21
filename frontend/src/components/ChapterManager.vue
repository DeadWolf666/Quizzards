<template>
  <div class="mt-3">
    <h6>Manage Chapters</h6>

    <ul class="list-group mb-3">
      <li
        class="list-group-item d-flex justify-content-between align-items-center"
        v-for="chapter in chapters"
        :key="chapter.id"
      >
        <div class="flex-grow-1">
          <span v-if="editingChapterId !== chapter.id">{{ chapter.name }}</span>
          <input
            v-else
            v-model="editedChapterName"
            class="form-control form-control-sm"
          />
        </div>

        <div class="ms-2">
          <button
            v-if="editingChapterId !== chapter.id"
            class="btn btn-sm btn-outline-secondary me-1"
            @click="startEditingChapter(chapter)"
          >
            Edit
          </button>

          <template v-else>
            <button
              class="btn btn-sm btn-success me-1"
              @click="saveEditedChapter(chapter.id)"
            >
              Save
            </button>
            <button
              class="btn btn-sm btn-secondary"
              @click="cancelEditingChapter"
            >
              Cancel
            </button>
          </template>

          <button
            class="btn btn-sm btn-outline-danger"
            @click="deleteChapter(chapter.id)"
          >
            Delete
          </button>
        </div>
      </li>
    </ul>

    <div class="input-group">
      <input
        type="text"
        class="form-control"
        v-model="newChapterName"
        placeholder="New chapter name"
      />
      <button class="btn btn-success" @click="addChapter">Add</button>
    </div>
  </div>
</template>

<script>
export default {
  name: "ChapterManager",
  props: ["subjectId"],
  data() {
    return {
      chapters: [],
      newChapterName: "",
      editingChapterId: null,
      editedChapterName: "",
    };
  },
  methods: {
    fetchChapters() {
      fetch(`/admin/subjects/${this.subjectId}/chapters`, {
        method: "GET",
        credentials: "include",
      })
        .then((res) => res.json())
        .then((data) => {
          this.chapters = data;
        })
        .catch((err) => {
          console.error("Error fetching chapters:", err);
        });
    },
    addChapter() {
      if (!this.newChapterName.trim()) {
        alert("Chapter name cannot be empty.");
        return;
      }

      fetch(`/admin/subjects/${this.subjectId}/chapters`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name: this.newChapterName }),
        credentials: "include",
      })
        .then((res) => res.json())
        .then(() => {
          this.newChapterName = "";
          this.fetchChapters();
          this.$emit("chapters-updated");
        })
        .catch((err) => {
          console.error("Error adding chapter:", err);
        });
    },
    deleteChapter(chapterId) {
      if (!confirm("Are you sure you want to delete this chapter?")) return;

      fetch(`/admin/chapters/${chapterId}`, {
        method: "DELETE",
        credentials: "include",
      })
        .then((res) => res.json())
        .then(() => {
          this.fetchChapters();
          this.$emit("chapters-updated");
        })
        .catch((err) => {
          console.error("Error deleting chapter:", err);
        });
    },
    startEditingChapter(chapter) {
      this.editingChapterId = chapter.id;
      this.editedChapterName = chapter.name;
    },
    cancelEditingChapter() {
      this.editingChapterId = null;
      this.editedChapterName = "";
    },
    async saveEditedChapter(chapterId) {
      try {
        const response = await fetch(`/admin/chapters/${chapterId}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: this.editedChapterName }),
        });

        if (!response.ok) {
          throw new Error("Failed to update chapter");
        }

        this.fetchChapters();
        this.cancelEditingChapter();
      } catch (error) {
        console.error(error);
        alert("Error updating chapter.");
      }
    },
  },
  mounted() {
    this.fetchChapters();
  },
  watch: {
    subjectId(newId, oldId) {
      if (newId !== oldId) this.fetchChapters();
    },
  },
};
</script>
