<template>
    <div>
        <main class="layout-main">
            <slot />
        </main>
    </div>
</template>

<style scoped>
.layout-container {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

.layout-main {
    flex: 1;
}
</style>
