<script setup>
defineProps({
  tasks: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: "",
  },
});

defineEmits(["delete"]);
</script>

<template>
  <section class="panel">
    <div class="panel-header">
      <h2>Task Dashboard</h2>
      <p>Saved tasks from SQLite.</p>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="loading" class="status">Loading tasks...</p>
    <p v-else-if="!tasks.length" class="status">No saved tasks yet.</p>

    <div v-else class="dashboard-list">
      <article v-for="task in tasks" :key="task.id" class="dashboard-card">
        <div class="dashboard-main">
          <h3>{{ task.title }}</h3>
          <p v-if="task.description">{{ task.description }}</p>
          <span class="meta">
            {{ task.category }} | {{ task.priority }} | {{ task.deadline || "No deadline" }}
          </span>
        </div>

        <button class="danger-button" @click="$emit('delete', task.id)">
          Delete
        </button>
      </article>
    </div>
  </section>
</template>

<style scoped>
.panel {
  background: #ffffff;
  border: 1px solid #dce6f0;
  border-radius: 18px;
  padding: 20px;
  box-shadow: 0 14px 40px rgba(33, 56, 82, 0.07);
}

.panel-header h2 {
  margin: 0 0 4px;
}

.panel-header p {
  margin: 0 0 16px;
  color: #5c7288;
}

.status,
.error {
  margin: 0;
}

.status {
  color: #607489;
}

.error {
  margin-bottom: 12px;
  color: #b42318;
}

.dashboard-list {
  display: grid;
  gap: 12px;
}

.dashboard-card {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  border: 1px solid #d8e3ee;
  border-radius: 14px;
  padding: 14px;
  background: #fbfdff;
}

.dashboard-main h3 {
  margin: 0 0 6px;
}

.dashboard-main p {
  margin: 0 0 8px;
  color: #4e6478;
}

.meta {
  display: inline-block;
  color: #607489;
  font-size: 0.95rem;
}

.danger-button {
  align-self: flex-start;
  border: 0;
  border-radius: 10px;
  padding: 10px 14px;
  background: #fee4e2;
  color: #b42318;
  cursor: pointer;
  font-weight: 600;
}

@media (max-width: 640px) {
  .dashboard-card {
    flex-direction: column;
  }

  .danger-button {
    width: 100%;
  }
}
</style>
