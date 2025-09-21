<template>
  <div class="d-flex">
    <SideBar @navigate="setView" />

    <div class="flex-grow-1 p-4">
      <h2>Admin Dashboard</h2>
      <div v-if="currentView === 'subjects'">
        <SubjectManager />
      </div>
      <div v-else-if="currentView === 'users'">
        <UserManager />
      </div>
      <div v-else-if="currentView === 'quizzes'">
        <QuizManager />
      </div>
      <div v-else>
        <p>Select an option from the sidebar.</p>
      </div>
    </div>
  </div>
</template>

<script>
import SideBar from "../components/SideBar.vue";
import SubjectManager from "../components/SubjectManager.vue";
import UserManager from "../components/UserManager.vue";
import QuizManager from "../components/QuizManager.vue";

export default {
  name: "AdminDashboard",
  components: {
    SideBar,
    SubjectManager,
    UserManager,
    QuizManager,
  },
  data() {
    return {
      currentView: "",
    };
  },
  methods: {
    setView(view) {
      this.currentView = view;
    },
  },
};
</script>
