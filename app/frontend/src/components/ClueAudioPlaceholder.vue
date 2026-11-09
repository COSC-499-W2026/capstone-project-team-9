<script setup>
// Static stand-in for the clue audio player until the backend serves clue audio.
// TODO: replace with the real player in the audio PR.

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
    <button type="button" class="player__button" disabled aria-label="Play clue (coming soon)">
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M8 5.6v12.8a1 1 0 0 0 1.5.86l10.2-6.4a1 1 0 0 0 0-1.72L9.5 4.74A1 1 0 0 0 8 5.6Z" />
      </svg>
    </button>

    <div class="player__wave" aria-hidden="true">
      <span v-for="(height, i) in bars" :key="i" class="player__bar" :style="{ '--h': height }" />
    </div>

    <p class="player__caption">Clue audio coming soon</p>
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
}

.player__caption {
  margin: -0.75rem 0 0;
  font-size: 0.8125rem;
  color: var(--text-muted);
}
</style>
