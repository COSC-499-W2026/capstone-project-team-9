<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import ClueAudioPlaceholder from '../components/ClueAudioPlaceholder.vue'
import { getPlayState } from '../api/game'
import '../styles/game.css'

const props = defineProps({
  playId: { type: [String, Number], required: true },
})

const router = useRouter()

const state = ref(null) // play state from GET /plays/{id}
const loadError = ref('')

// Positions can have gaps, so number clues by how many are already solved
const clueNumber = computed(() => Math.min(state.value.solved_clues + 1, state.value.total_clues))
const progress = computed(() =>
  state.value.total_clues ? state.value.solved_clues / state.value.total_clues : 0,
)

async function load() {
  loadError.value = ''
  try {
    state.value = await getPlayState(props.playId)
  } catch (err) {
    loadError.value = err.status === 404 ? "This game doesn't exist." : "Couldn't load your game."
  }
}

onMounted(load)

const exit = () => router.push({ name: 'play' })
</script>

<template>
  <!-- .game is the full-screen layer with the background; .stage centres the content column -->
  <div class="game">
    <div class="stage">
      <!-- Top bar: exit + progress -->
      <header class="topbar">
        <button type="button" class="topbar__exit" aria-label="Exit game" @click="exit">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18" /></svg>
        </button>
        <div v-if="state && !state.completed" class="topbar__progress">
          <span class="topbar__count">Clue {{ clueNumber }} of {{ state.total_clues }}</span>
          <div class="bar" role="progressbar" :aria-valuenow="state.solved_clues" :aria-valuemax="state.total_clues">
            <div class="bar__fill" :style="{ transform: `scaleX(${progress})` }" />
          </div>
        </div>
        <span class="topbar__spacer" />
      </header>

      <!-- Loading / error -->
      <div v-if="!state && !loadError" class="center">
        <span class="spinner spinner--large" aria-label="Loading" />
      </div>

      <div v-else-if="loadError" class="center center--column">
        <p class="muted">{{ loadError }}</p>
        <button type="button" class="btn btn--secondary" @click="exit">Back to start</button>
      </div>

      <!-- Finished -->
      <section v-else-if="state.completed" class="done">
        <div class="done__badge" aria-hidden="true">
          <svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5" /></svg>
        </div>
        <h1 class="done__title">You found them all.</h1>
        <p class="muted">All {{ state.total_clues }} clues solved. Nicely done.</p>
        <button type="button" class="btn btn--primary" @click="exit">Play again</button>
      </section>

      <!-- Current clue -->
      <Transition v-else name="slide" mode="out-in" appear>
        <section :key="state.current_clue_id" class="clue">
          <div class="card">
            <p class="card__eyebrow">Listen</p>
            <ClueAudioPlaceholder />
          </div>

          <!-- TODO: enable once the backend has a skip endpoint, then call load() to show the next clue -->
          <button type="button" class="btn btn--secondary btn--block" disabled title="Skipping isn't available yet">
            Skip
            <svg class="skip-icon" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M5 6.5v11a1 1 0 0 0 1.6.8l7.3-5.5a1 1 0 0 0 0-1.6L6.6 5.7A1 1 0 0 0 5 6.5Z" />
              <rect x="16" y="5.5" width="2.6" height="13" rx="1.1" />
            </svg>
          </button>
        </section>
      </Transition>
    </div>
  </div>
</template>

<style scoped>
.stage {
  min-height: 100vh;
  min-height: 100dvh;
  max-width: 34rem;
  margin: 0 auto;
  padding: 0 1rem calc(2rem + env(safe-area-inset-bottom));
  display: flex;
  flex-direction: column;
}

/* ---------- Top bar ---------- */
.topbar {
  position: sticky;
  top: 0;
  z-index: 5;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: calc(0.75rem + env(safe-area-inset-top)) 0 0.75rem;
}

.topbar__exit {
  display: grid;
  place-items: center;
  width: 2.25rem;
  height: 2.25rem;
  flex-shrink: 0;
  border: none;
  border-radius: 50%;
  background: var(--surface);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: var(--shadow);
}

.topbar__exit svg {
  width: 1rem;
  height: 1rem;
  stroke: var(--text-muted);
  stroke-width: 2.4;
  stroke-linecap: round;
}

.topbar__progress {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.topbar__count {
  font-size: 0.8125rem;
  font-weight: 600;
  text-align: center;
  color: var(--text-muted);
}

.topbar__spacer {
  width: 2.25rem;
  flex-shrink: 0;
}

.bar {
  height: 4px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--surface-sunken);
}

.bar__fill {
  height: 100%;
  background: var(--accent);
  border-radius: inherit;
  transform-origin: left;
  transition: transform 0.6s var(--ease);
}

/* ---------- Clue ---------- */
.clue {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-top: 1rem;
}

.card {
  padding: 1.5rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--surface);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  box-shadow: var(--shadow);
}

.card__eyebrow {
  margin: 0 0 1.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent);
}

.skip-icon {
  width: 1rem;
  height: 1rem;
  fill: currentColor;
}

.muted {
  color: var(--text-muted);
}

/* ---------- States ---------- */
.center {
  flex: 1;
  display: grid;
  place-items: center;
}

.center--column {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 1rem;
}

.spinner--large {
  width: 2rem;
  height: 2rem;
  color: var(--text-faint);
}

.done {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  text-align: center;
  animation: rise 0.7s var(--ease) both;
}

.done__badge {
  display: grid;
  place-items: center;
  width: 6rem;
  height: 6rem;
  margin-bottom: 1.5rem;
  border-radius: 50%;
  background: var(--success);
  box-shadow: 0 16px 40px -10px var(--success);
  animation: badge 0.7s 0.15s var(--ease) both;
}

.done__badge svg {
  width: 55%;
  height: 55%;
  fill: none;
  stroke: #fff;
  stroke-width: 2.6;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.done__title {
  margin: 0;
  font-size: clamp(2.25rem, 8vw, 3rem);
  font-weight: 700;
}

.done .btn {
  margin-top: 1.5rem;
  min-width: 12rem;
}

/* ---------- Transitions ---------- */
.slide-enter-active,
.slide-leave-active {
  transition:
    opacity 0.4s var(--ease),
    transform 0.4s var(--ease);
}

.slide-enter-from {
  opacity: 0;
  transform: translateX(32px);
}

.slide-leave-to {
  opacity: 0;
  transform: translateX(-32px);
}

@keyframes rise {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
}

@keyframes badge {
  from {
    opacity: 0;
    transform: scale(0.4);
  }
}

</style>
