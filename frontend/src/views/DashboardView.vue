<script setup>
const investigationCards = [
    {
        id: "q1",
        icon: "⛴️",
        title: "Which vessels deliver which products and when?",
    },
    {
        id: "q2",
        icon: "🐟",
        title: "How did SouthSeafood Express Corp perform illegal fishing?",
    },
    {
        id: "q3",
        icon: "🧭",
        title: "Which other vessels show similar behavior?",
    },
    {
        id: "q4",
        icon: "📉",
        title: "How did fishing activity change afterward?",
    },
];
</script>

<template>
    <section class="intro-page">
        <div class="intro-content">
            <header class="intro-header">
                <span class="intro-icon" aria-hidden="true">🚢</span>
                <p class="intro-label">Oceanus Visual Analytics System</p>
            </header>

            <div class="intro-hero">
                <p>FishEye analysts use Oceanus to uncover patterns in vessel movements, cargo flows, and suspicious fishing activity.</p>
                <p>Explore how vessels interact with ports, products, and habitats to detect illegal behavior.</p>
            </div>

            <div class="intro-cards">
                <article v-for="card in investigationCards" :key="card.id" class="intro-card">
                    <div class="intro-card-icon" aria-hidden="true">{{ card.icon }}</div>
                    <h3>{{ card.title }}</h3>
                    <p>{{ card.subtitle }}</p>
                </article>
            </div>

            <router-link class="intro-cta" to="/question1">
                Start Analysis
            </router-link>
        </div>
    </section>
</template>

<style scoped>
:global(body) {
    background: radial-gradient(circle at top, rgba(2, 132, 199, 0.08), transparent 55%);
}

.intro-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 4rem 1.5rem;
    background: radial-gradient(circle at top, rgba(2, 132, 199, 0.08), transparent 55%);
}

.intro-content {
    width: min(960px, 100%);
    text-align: center;
    display: flex;
    flex-direction: column;
    gap: 2.5rem;
}

.intro-header {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    font-weight: 600;
    color: #0e7490;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 0.95rem;
}

.intro-icon {
    font-size: 1.25rem;
}

.intro-hero {
    font-size: clamp(1.4rem, 2.5vw, 1.8rem);
    font-weight: 500;
    color: #0f172a;
    line-height: 1.5;
}

.intro-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1.25rem;
}

.intro-card {
    background: #ffffff;
    padding: 1.75rem;
    border: 1px solid rgba(15, 23, 42, 0.08);
    border-radius: 1rem;
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.08);
    transition: transform 200ms ease, box-shadow 200ms ease;
    text-align: left;
}

.intro-card h3 {
    font-size: 1.05rem;
    margin-bottom: 0.6rem;
    color: #0f172a;
}

.intro-card p {
    color: #475569;
    font-size: 0.95rem;
    line-height: 1.4;
}

.intro-card-icon {
    font-size: 1.8rem;
    margin-bottom: 0.75rem;
}

.intro-card:hover {
    transform: translateY(-6px) scale(1.01);
    box-shadow: 0 16px 32px rgba(15, 23, 42, 0.12);
}

.intro-cta {
    align-self: center;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.95rem 2.5rem;
    border-radius: 999px;
    background: linear-gradient(120deg, #0e7490, #0284c7);
    color: #ffffff;
    font-weight: 600;
    font-size: 1rem;
    text-decoration: none;
    box-shadow: 0 12px 24px rgba(2, 132, 199, 0.35);
    transition: transform 200ms ease, box-shadow 200ms ease;
}

.intro-cta:hover {
    transform: translateY(-4px);
    box-shadow: 0 18px 32px rgba(2, 132, 199, 0.45);
}

@media (max-width: 640px) {
    .intro-hero {
        font-size: 1.25rem;
    }

    .intro-card {
        padding: 1.5rem;
    }
}
</style>
