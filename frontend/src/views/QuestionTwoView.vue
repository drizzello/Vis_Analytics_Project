<script setup>
import { onMounted } from "vue";
import { fetchFilters } from "@/stores/usefilters.js";
import VesselsRoutineTimeline from "@/components/VesselsRoutineTimeline.vue";
import DwellComparisonLine from "@/components/DwellComparisonLine.vue";
import PageFilters from "@/components/PageFilters.vue";

onMounted(() => {
  fetchFilters();
});
</script>

<template>
  <section class="question-page">
    <!-- INTRO -->
    <article class="question-card question-card--intro">
      <header class="question-header">
        <div class="question-title">
          <p class="question-eyebrow">Investigation 2</p>
          <h1>Suspicious activity patterns</h1>
        </div>
        <div class="question-nav">
          <RouterLink class="nav-button ghost" to="/question1">← Back to Question 1</RouterLink>
          <RouterLink class="nav-button primary" to="/question2">
            Continue the Investigation →
          </RouterLink>
        </div>
      </header>

      <!-- ⚓️ Custom Filter: Vessel Only -->
      <PageFilters :show-port="false" :show-date="false" :show-vessel="true" />
    </article>

    <!-- TIMELINE VISUALIZATION -->
    <article class="question-card question-card--visual">
      <div class="question-section-heading">
        <div>
          <p class="section-eyebrow">Vessels & dwell time</p>
          <h2>When and where did SouthSeafood Express vessels operate illegally?</h2>
        </div>
        <p class="section-context">
          Timeline shows all visited areas for the selected vessel.
          Colors indicate the area type: fishing, preserve, city, or buoy.
        </p>
      </div>
      <VesselsRoutineTimeline />
    </article>

    <article class="question-card question-card--visual">
      <div class="question-section-heading">
        <div>
          <p class="section-eyebrow">Vessels & dwell time</p>
          <h2>Average Dwell by Zone — Behavioral Comparison</h2>
        </div>
        <p class="section-context">
          Compare the selected vessel’s activity against the fleet baseline.
          The shaded area represents the normal operating range (safe zone, 25th–75th percentile),
          while the blue line highlights deviations that may indicate suspicious or abnormal behavior.
        </p>
      </div>
      <DwellComparisonLine />
    </article>

  </section>
</template>

<style scoped>
.question-card--intro {
  gap: 1.5rem;
}

.question-card--visual {
  padding: clamp(1.5rem, 2.5vw, 2.5rem);
}

.section-eyebrow {
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 0.12em;
  color: #0e7490;
  margin-bottom: 0.35rem;
}

h2 {
  margin: 0.25rem 0 0.75rem;
  color: #0f172a;
}
</style>
