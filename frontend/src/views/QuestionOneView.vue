<script setup>
import PageFilters from "@/components/PageFilters.vue";
import VesselDwellScatter from "@/components/VesselDwellScatter.vue";
import DailyExportsBar from "@/components/DailyExport.vue";
import VesselCatchBar from "@/components/VesselCatchBar.vue";
</script>

<template>
  <section class="question-page">
    <!-- INTRO -->
    <article class="question-card question-card--intro">
      <header class="question-header">
        <div class="question-title">
          <p class="question-eyebrow">Investigation 1</p>
          <h1>Which vessels deliver which products and when?</h1>
        </div>
        <div class="question-nav">
          <RouterLink class="nav-button ghost" to="/">← Back to Overview</RouterLink>
          <RouterLink class="nav-button primary" to="/question2">
            Continue the Investigation →
          </RouterLink>
        </div>
      </header>

      <PageFilters />
    </article>

    <!-- VIS 1: DWELL SCATTER -->
    <article class="question-card question-card--visual">
      <div class="question-section-heading">
        <div>
          <p class="section-eyebrow">Routes & dwell time</p>
          <h2>How long did each vessel remain across the route?</h2>
        </div>
        <p class="section-context">
          Bubble size encodes dwell time while color separates protected vs non-protected areas.
          Toggle ports/dates above to focus on specific arrivals.
        </p>
      </div>
      <VesselDwellScatter />
    </article>

    <!-- VIS 2: DECLARED EXPORTS -->
    <article class="question-card question-card--visual">
      <div class="question-section-heading">
        <div>
          <p class="section-eyebrow">Declared exports</p>
          <h2>Which products were unloaded on the day after?</h2>
        </div>
        <p class="section-context">
          Compare exported tons per fish species to match the vessels that could legally ship them.
        </p>
      </div>
      <DailyExportsBar />
    </article>

<!-- FORMULA / EXPLANATION -->
<article class="question-card question-card--formula">
  <div class="formula-box">
    <p class="section-eyebrow">Estimation model</p>
    <h2>How are cargo loads distributed among vessels?</h2>

    <p class="formula-explanation">
      For each <strong>cargo</strong> exported from a port, the system first identifies its
      <strong>fish species</strong> and the <strong>habitat locations</strong> where that fish normally occurs.
      Then, it selects all vessels that operated in those locations before the cargo’s departure day.
      <br /><br />
      Each vessel’s contribution is weighted by its <strong>tonnage × dwell time</strong>
      within the relevant fishing zones. The cargo’s total exported weight is then distributed
      proportionally among these vessels:
    </p>

    <pre class="formula-code">
estimated_tonsᵢ = exports_tons(cargoⱼ, fishₖ) ×
   ( tonnageᵢ × dwellᵢ ) / Σ( tonnage × dwell )₍ⱼ,ₖ₎
    </pre>

    <p class="formula-note">
      This calculation links <em>each cargo</em> to <em>its likely source vessels</em>,
      accounting for both vessel capacity and time spent fishing in relevant habitats.
      When multiple cargos are present, the same rule is applied independently to
      every <strong>cargo → fish → vessel</strong> combination.
    </p>
  </div>
</article>

    <!-- VIS 3: VESSEL CATCH -->
    <article class="question-card question-card--visual">
      <VesselCatchBar />
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

.question-card--formula {
  padding: 2rem;
  background-color: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

.formula-box {
  max-width: 720px;
  margin: auto;
  text-align: left;
}

.formula-code {
  background: #0f172a;
  color: #e2e8f0;
  padding: 1rem;
  border-radius: 8px;
  font-family: "Fira Code", monospace;
  font-size: 0.95rem;
  white-space: pre;
  margin-top: 0.5rem;
}

.formula-explanation {
  color: #475569;
  margin-bottom: 0.5rem;
  line-height: 1.6;
}

.formula-note {
  color: #64748b;
  margin-top: 0.8rem;
  font-size: 0.9rem;
  font-style: italic;
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
