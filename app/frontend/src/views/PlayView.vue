<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { verifyLocation } from '../api/location'
import { getDifficulties, getGameLengths, getLanguages, startGame } from '../api/game'
import { getCurrentCoords } from '../utils/geolocation'

const DEFAULT_NUM_CLUES = 3

const router = useRouter()

const result = ref(null)
const error = ref('')
const loading = ref(false)

const languages = ref([])
const difficulties = ref([])
const languageId = ref(null)
const difficultyId = ref(null)
const lengths = ref(null) // {min, max} clues available for the selected language + difficulty
const numClues = ref(null)

// Every question count the player can pick, e.g. [1, 2, 3, 4]
const clueCounts = computed(() => {
  if (!lengths.value?.max) return []
  const { min, max } = lengths.value
  return Array.from({ length: max - min + 1 }, (_, i) => min + i)
})

onMounted(async () => {
  try {
    const [langs, diffs] = await Promise.all([getLanguages(), getDifficulties()])
    languages.value = langs
    difficulties.value = diffs
    difficultyId.value = diffs[0]?.id ?? null
    languageId.value = langs[0]?.id ?? null
  } catch {
    error.value = "Couldn't load game options."
  }
})

watch([languageId, difficultyId], async ([lang, diff]) => {
  lengths.value = null
  numClues.value = null
  if (lang == null || diff == null) return
  try {
    const range = await getGameLengths(lang, diff)
    if (lang !== languageId.value || diff !== difficultyId.value) return // selection changed while this loaded
    lengths.value = range
    if (range.max > 0) numClues.value = Math.min(Math.max(DEFAULT_NUM_CLUES, range.min), range.max)
  } catch {
    error.value = "Couldn't check how many questions are available."
  }
})

async function play() {
  error.value = ''
  result.value = null
  loading.value = true
  try {
    const { latitude, longitude } = await getCurrentCoords()
    result.value = await verifyLocation(latitude, longitude)
    if (result.value.allowed) {
      if (!numClues.value) throw new Error('No questions available for this language and difficulty yet.')
      const playId = await startGame({
        languageId: languageId.value,
        difficultyId: difficultyId.value,
        numClues: numClues.value,
      })
      await router.push({ name: 'clue', params: { playId } })
    }
  } catch (err) {
    error.value = err.detail ?? err.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section>
    <button :disabled="loading" @click="play">Play</button>

    <div>
      <label for="language">Language: </label>
      <select id="language" v-model="languageId">
        <option v-for="language in languages" :key="language.id" :value="language.id">
          {{ language.name }}
        </option>
      </select>
    </div>

    <div>
      <label for="difficulty">Difficulty: </label>
      <select id="difficulty" v-model="difficultyId">
        <option v-for="difficulty in difficulties" :key="difficulty.id" :value="difficulty.id">
          {{ difficulty.name }}
        </option>
      </select>
    </div>

    <div>
      <label for="num-clues">Questions: </label>
      <select id="num-clues" v-model="numClues" :disabled="!clueCounts.length">
        <option v-if="!clueCounts.length" :value="null">None available</option>
        <option v-for="count in clueCounts" :key="count" :value="count">{{ count }}</option>
      </select>
    </div>

    <p v-if="result">{{ result.allowed ? '✅' : '🚫' }} {{ result.message }}</p>
    <p v-if="error">Error: {{ error }}</p>
  </section>
</template>
