<script setup>
import { onMounted, ref } from "vue";

import ParsedTasks from "./components/ParsedTasks.vue";
import TaskInput from "./components/TaskInput.vue";
import TaskList from "./components/TaskList.vue";
import { createTask, deleteTask, getTasks } from "./services/api";

const parsedTasks = ref([]);
const tasks = ref([]);
const loadingTasks = ref(false);
const dashboardError = ref("");
const saving = ref(false);

const loadTasks = async () => {
  loadingTasks.value = true;
  dashboardError.value = "";

  try {
    const response = await getTasks();
    tasks.value = response.tasks ?? [];
  } catch (error) {
    dashboardError.value =
      error.response?.data?.details || "Unable to load saved tasks.";
  } finally {
    loadingTasks.value = false;
  }
};

const handleParsed = (items) => {
  parsedTasks.value = items;
};

const handleSaveParsedTasks = async () => {
  if (!parsedTasks.value.length) {
    return;
  }

  saving.value = true;
  dashboardError.value = "";

  try {
    await createTask({ tasks: parsedTasks.value });
    parsedTasks.value = [];
    await loadTasks();
  } catch (error) {
    dashboardError.value =
      error.response?.data?.details || "Unable to save parsed tasks.";
  } finally {
    saving.value = false;
  }
};

const handleDeleteTask = async (taskId) => {
  dashboardError.value = "";

  try {
    await deleteTask(taskId);
    await loadTasks();
  } catch (error) {
    dashboardError.value =
      error.response?.data?.details || "Unable to delete the task.";
  }
};

onMounted(() => {
  loadTasks();
});
</script>

<template>
  <main class="app-shell">
    <section class="hero">
      <div>
        <p class="eyebrow">AI Task Manager Agent</p>
        <h1>Turn messy notes into clean, actionable tasks.</h1>
        <p class="intro">
          Paste rough task ideas, let Claude structure them, validate the result
          with Pydantic, and save them to your dashboard.
        </p>
      </div>
    </section>

    <section class="grid">
      <TaskInput @parsed="handleParsed" />
      <ParsedTasks
        :tasks="parsedTasks"
        :saving="saving"
        @save="handleSaveParsedTasks"
      />
    </section>

    <TaskList
      :tasks="tasks"
      :loading="loadingTasks"
      :error="dashboardError"
      @delete="handleDeleteTask"
    />
  </main>
</template>

<style>
:root {
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  color: #15202b;
  background: linear-gradient(180deg, #f5f7fb 0%, #eef3f8 100%);
  line-height: 1.5;
  font-weight: 400;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-width: 320px;
}

button,
textarea {
  font: inherit;
}

.app-shell {
  max-width: 1080px;
  margin: 0 auto;
  padding: 32px 20px 48px;
}

.hero {
  margin-bottom: 24px;
}

.eyebrow {
  margin: 0 0 8px;
  font-size: 0.9rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #4c6b8a;
  font-weight: 700;
}

h1 {
  margin: 0 0 10px;
  font-size: clamp(2rem, 4vw, 3rem);
  line-height: 1.1;
}

.intro {
  max-width: 680px;
  margin: 0;
  color: #4f657a;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

@media (max-width: 640px) {
  .app-shell {
    padding: 20px 14px 32px;
  }
}
</style>
