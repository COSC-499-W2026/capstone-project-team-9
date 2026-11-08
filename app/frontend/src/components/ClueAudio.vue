<script setup>
import { computed, ref, watch } from 'vue'

/** Audio clue player: a big play button over a waveform that fills as the clip plays. */
const props = defineProps({
  src: { type: String, required: true },
})

const BAR_COUNT = 36

const audio = ref(null)
const playing = ref(false)
const current = ref(0)
const duration = ref(0)
const unavailable = ref(false)

// Deterministic "waveform" so it doesn't jump around between renders
const bars = computed(() => {
  let seed = [...props.src].reduce((sum, ch) => sum + ch.charCodeAt(0), 0)
  return Array.from({ length: BAR_COUNT }, (_, i) => {
    seed = (seed * 9301 + 49297) % 233280
    const envelope = Math.sin((Math.PI * (i + 0.5)) / BAR_COUNT) // taller in the middle
    return 0.25 + 0.75 * envelope * (0.45 + 0.55 * (seed / 233280))
  })
})

const progress = computed(() => (duration.value ? current.value / duration.value : 0))

watch(
  () => props.src,
  () => {
    playing.value = false
    current.value = 0
    duration.value = 0
    unavailable.value = false
  },
)

function formatTime(seconds) {
  if (!Number.isFinite(seconds)) return '0:00'
  const s = Math.floor(seconds)
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`
}

async function toggle() {
  const el = audio.value
  if (!el || unavailable.value) return
  if (playing.value) {
    el.pause()
    return
  }
  try {
    await el.play()
  } catch {
    unavailable.value = true
  }
}

function seek(i) {
  const el = audio.value
  if (!el || !duration.value) return
  el.currentTime = (i / BAR_COUNT) * duration.value
  current.value = el.currentTime
}

function onLoaded() {
  duration.value = audio.value.duration
}

function onEnded() {
  playing.value = false
  current.value = 0
}
</script>

<template>
  <div class="player" :class="{ 'is-playing': playing, 'is-unavailable': unavailable }">
    <audio
      ref="audio"
      :src="src"
      preload="metadata"
      @loadedmetadata="onLoaded"
      @timeupdate="current = audio.currentTime"
      @play="playing = true"
      @pause="playing = false"
      @ended="onEnded"
      @error="unavailable = true"
    />

    <button
      type="button"
      class="player__button"
      :disabled="unavailable"
      :aria-label="playing ? 'Pause clue' : 'Play clue'"
      @click="toggle"
    >
      <span class="player__ring" aria-hidden="true" />
      <svg v-if="playing" viewBox="0 0 24 24" aria-hidden="true">
        <rect x="6" y="5" width="4" height="14" rx="1.2" />
        <rect x="14" y="5" width="4" height="14" rx="1.2" />
      </svg>
      <svg v-else viewBox="0 0 24 24" aria-hidden="true">
        <path d="M8 5.6v12.8a1 1 0 0 0 1.5.86l10.2-6.4a1 1 0 0 0 0-1.72L9.5 4.74A1 1 0 0 0 8 5.6Z" />
      </svg>
    </button>

    <div class="player__wave" aria-hidden="true">
      <span
        v-for="(height, i) in bars"
        :key="i"
        class="player__bar"
        :class="{ 'is-filled': i / bars.length < progress }"
        :style="{ '--h': height, '--i': i }"
        @click="seek(i)"
      />
    </div>

    <div class="player__meta">
      <template v-if="unavailable">Audio isn't available for this clue yet</template>
      <template v-else>
        <span>{{ formatTime(current) }}</span>
        <span>{{ formatTime(duration) }}</span>
      </template>
    </div>
  </div>
</template>

<style scoped>
.player {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.player__button {
  position: relative;
  display: grid;
  place-items: center;
  width: 5.5rem;
  height: 5.5rem;
  border: none;
  border-radius: 50%;
  background: var(--accent);
  color: var(--on-accent);
  box-shadow: 0 12px 32px -8px var(--accent);
  transition: transform 0.25s var(--ease);
}

.player__button:active:not(:disabled) {
  transform: scale(0.94);
}

.player__button:disabled {
  background: var(--surface-sunken);
  color: var(--text-faint);
  box-shadow: none;
}

.player__button svg {
  width: 2.25rem;
  height: 2.25rem;
  fill: currentColor;
}

/* Soft pulsing halo while the clue plays */
.player__ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 2px solid var(--accent);
  opacity: 0;
}

.is-playing .player__ring {
  animation: halo 1.6s var(--ease) infinite;
}

@keyframes halo {
  0% {
    transform: scale(1);
    opacity: 0.5;
  }
  100% {
    transform: scale(1.6);
    opacity: 0;
  }
}

.player__wave {
  display: flex;
  align-items: center;
  gap: 3px;
  width: 100%;
  height: 3rem;
}

.player__bar {
  flex: 1;
  height: calc(var(--h) * 100%);
  min-width: 2px;
  border-radius: 999px;
  background: var(--text-faint);
  opacity: 0.45;
  cursor: pointer;
  transition:
    background-color 0.15s ease,
    opacity 0.15s ease;
}

.player__bar.is-filled {
  background: var(--accent);
  opacity: 1;
}

.is-playing .player__bar {
  animation: bob 1.2s ease-in-out infinite;
  animation-delay: calc(var(--i) * -70ms);
}

@keyframes bob {
  50% {
    transform: scaleY(0.7);
  }
}

.is-unavailable .player__bar {
  cursor: default;
  opacity: 0.2;
}

.player__meta {
  display: flex;
  justify-content: space-between;
  width: 100%;
  margin-top: -0.75rem;
  font-size: 0.8125rem;
  font-variant-numeric: tabular-nums;
  color: var(--text-muted);
}

.is-unavailable .player__meta {
  justify-content: center;
}
</style>
