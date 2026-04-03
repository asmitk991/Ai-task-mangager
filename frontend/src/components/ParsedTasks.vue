<script setup>
defineProps({
  tasks: {
    type: Array,
    default: () => [],
  },
  saving: {
    type: Boolean,
    default: false,
  },
});

defineEmits(["save"]);
</script>

<template>
  <section class="panel">
    <div class="panel-header">
      <h2>Parsed Output</h2>
      <p>Validated tasks ready to save.</p>
    </div>

    <div v-if="!tasks.length" class="empty-state">
      No parsed tasks yet. Run the parser to see structured output.
    </div>

    <div v-else class="task-stack">
      <article v-for="(task, index) in tasks" :key="`${task.title}-${index}`" class="task-card">
        <h3>{{ task.title }}</h3>
        <p v-if="task.description" class="description">{{ task.description }}</p>
        <dl>
          <div>
            <dt>Deadline</dt>
            <dd>{{ task.deadline || "Not set" }}</dd>
          </div>
          <div>
            <dt>Priority</dt>
            <dd>{{ task.priority }}</dd>
          </div>
          <div>
            <dt>Category</dt>
            <dd>{{ task.category }}</dd>
          </div>
        </dl>
      </article>

      <button class="primary-button" :disabled="saving" @click="$emit('save')">
        {{ saving ? "Saving..." : "Save Tasks" }}
      </button>
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

.empty-state {
  min-height: 180px;
  display: grid;
  place-items: center;
  text-align: center;
  color: #667b90;
  border: 1px dashed #cfdbe7;
  border-radius: 14px;
  padding: 20px;
  background: #fbfdff;
}

.task-stack {
  display: grid;
  gap: 12px;
}

.task-card {
  border: 1px solid #d8e3ee;
  border-radius: 14px;
  padding: 14px;
  background: #fbfdff;
}

.task-card h3 {
  margin: 0 0 8px;
  font-size: 1.05rem;
}

.description {
  margin: 0 0 12px;
  color: #4e6478;
}

dl {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin: 0;
}

dt {
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #678096;
}

dd {
  margin: 4px 0 0;
  font-weight: 600;
}

.primary-button {
  border: 0;
  border-radius: 12px;
  padding: 12px 16px;
  background: #17324d;
  color: #fff;
  cursor: pointer;
  font-weight: 600;
}

.primary-button:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

@media (max-width: 520px) {
  dl {
    grid-template-columns: 1fr;
  }
}
</style>
