<script setup>
import { ref } from "vue";

import { parseTask } from "../services/api";

const emit = defineEmits(["parsed"]);

const input = ref("");
const loading = ref(false);
const error = ref("");

const handleSubmit = async () => {
  error.value = "";

  if (!input.value.trim()) {
    error.value = "Enter a natural-language task description first.";
    return;
  }

  loading.value = true;

  try {
    const response = await parseTask(input.value);
    emit("parsed", response.tasks ?? []);
  } catch (err) {
    error.value = err.response?.data?.details || "Unable to parse tasks right now.";
    emit("parsed", []);
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <section class="panel">
    <div class="panel-header">
      <h2>Task Input</h2>
      <p>Paste rough notes, deadlines, or mixed task ideas.</p>
    </div>

    <textarea
      v-model="input"
      rows="10"
      placeholder="Example: Finish landing page by next Friday, book dentist appointment, and prepare Q2 budget review."
    />

    <button class="primary-button" :disabled="loading" @click="handleSubmit">
      {{ loading ? "Parsing..." : "Parse Task" }}
    </button>

    <p v-if="error" class="error">{{ error }}</p>
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

textarea {
  width: 100%;
  padding: 14px;
  border-radius: 14px;
  border: 1px solid #cfdbe7;
  resize: vertical;
  background: #fbfdff;
  color: #142230;
}

.primary-button {
  margin-top: 14px;
  width: 100%;
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

.error {
  margin: 12px 0 0;
  color: #b42318;
}
</style>
