<script setup>
import { onBeforeUnmount, ref, watch } from 'vue'
import { get } from '../api/client'
import { fetchClueAudio } from '../api/clue'

const props = defineProps({
  clueId: { type: Number, required: true },
})

const audio = ref(null)
const audioUrl = ref('') // object URL for the downloaded mp3
const status = ref('loading') // loading | ready | error
const errorMessage = ref('')
const playing = ref(false)
const progress = ref(0) // 0 to 1

function revokeUrl() {
  if (audioUrl.value) URL.revokeObjectURL(audioUrl.value)
  audioUrl.value = ''
}

async function load() {
  const clueId = props.clueId
  revokeUrl()
  playing.value = false
  progress.value = 0
  errorMessage.value = ''
  status.value = 'loading'
  try {
    const blob = await fetchClueAudio(clueId)
    if (clueId !== props.clueId) return // a newer clue replaced this one while loading
    audioUrl.value = URL.createObjectURL(blob)
    status.value = 'ready'
  } catch (err) {
    if (clueId !== props.clueId) return
    errorMessage.value = err.status === 404 ? 'No audio for this clue yet.' : "Couldn't load the audio."
    status.value = 'error'
  }
}

// Download on mount and whenever the clue changes
watch(() => props.clueId, load, { immediate: true })

async function toggle() {
  errorMessage.value = ''
  if (playing.value) {
    audio.value.pause()
    return
  }
  try {
    await audio.value.play()
  } catch {
    errorMessage.value = "Couldn't play the audio."
  }
}

function updateProgress() {
  const { currentTime, duration } = audio.value
  progress.value = duration ? currentTime / duration : 0
}

function onEnded() {
  playing.value = false
  progress.value = 0
}

onBeforeUnmount(revokeUrl)

// TESTING ONLY: show which room this clue points to, so testers know which sign to photograph.
// The endpoint only exists when the backend runs with ENV=development; otherwise nothing shows.
const testRoom = ref('')
watch(
  () => props.clueId,
  async (clueId) => {
    testRoom.value = ''
    try {
      testRoom.value = (await get(`/dev/clues/${clueId}/room`)).room
    } catch {
      // not in development
    }
  },
  { immediate: true },
)

const BAR_COUNT = 36

// Fixed "waveform" shape: taller in the middle, with some deterministic variation
let seed = 7
const bars = Array.from({ length: BAR_COUNT }, (_, i) => {
  seed = (seed * 9301 + 49297) % 233280
  const envelope = Math.sin((Math.PI * (i + 0.5)) / BAR_COUNT)
  return 0.25 + 0.75 * envelope * (0.45 + 0.55 * (seed / 233280))
})
</script>

<template>
  <div class="player">
    <button
      type="button"
      class="player__button"
      :disabled="status !== 'ready'"
      :aria-label="playing ? 'Pause clue' : 'Play clue'"
      @click="toggle"
    >
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
        :class="{ 'player__bar--played': (i + 1) / BAR_COUNT <= progress }"
        :style="{ '--h': height }"
      />
    </div>

    <audio
      v-if="audioUrl"
      ref="audio"
      :src="audioUrl"
      preload="auto"
      @play="playing = true"
      @pause="playing = false"
      @ended="onEnded"
      @timeupdate="updateProgress"
    />

    <p v-if="status === 'loading'" class="player__caption">Loading audio…</p>
    <p v-else-if="status === 'ready' && !errorMessage" class="player__caption">Tap to listen. Replay as often as you like.</p>

    <p v-if="errorMessage" class="player__error" role="alert">{{ errorMessage }}</p>
    <button v-if="status === 'error'" type="button" class="btn btn--secondary" @click="load">Retry</button>

    <p v-if="testRoom" class="player__test-room">Test mode · Room <strong>{{ testRoom }}</strong></p>
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
  display: grid;
  place-items: center;
  width: 5.5rem;
  height: 5.5rem;
  border: none;
  border-radius: 50%;
  background: var(--accent-soft);
  color: var(--accent);
  transition: transform 0.2s var(--ease);
}

.player__button:active:not(:disabled) {
  transform: scale(0.94);
}

.player__button:disabled {
  background: var(--surface-sunken);
  color: var(--text-faint);
}

.player__button svg {
  width: 2.25rem;
  height: 2.25rem;
  fill: currentColor;
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
  opacity: 0.2;
  transition: opacity 0.2s ease, background-color 0.2s ease;
}

.player__bar--played {
  background: var(--accent);
  opacity: 0.9;
}

.player__caption {
  margin: -0.75rem 0 0;
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.player__error {
  margin: -0.75rem 0 0;
  padding: 0.5rem 0.85rem;
  border-radius: var(--radius-sm);
  background: var(--danger-soft);
  color: var(--danger);
  font-size: 0.875rem;
}

.player__test-room {
  margin: -1rem 0 0;
  padding: 0.35rem 0.85rem;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent);
  font-size: 0.8125rem;
}
</style>