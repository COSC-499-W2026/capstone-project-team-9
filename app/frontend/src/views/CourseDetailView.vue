<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getAccessCode, getMyCourse } from '../api/course'
import { getLanguages } from '../api/game'

const props = defineProps({
  courseId: { type: [String, Number], required: true },
})

const router = useRouter()

const course = ref(null)
const languages = ref([])
const loading = ref(true)
const error = ref('')
const accessCode = ref('')

const languageName = computed(
  () => languages.value.find((l) => l.id === course.value?.language_id)?.name ?? 'Unknown language',
)

onMounted(async () => {
  try {
    const [found, langs] = await Promise.all([getMyCourse(props.courseId), getLanguages()])
    languages.value = langs
    course.value = found
    if (!found) error.value = "Course not found, or you're not enrolled in it."
  } catch (err) {
    if (err.status === 401) {
      await router.push({ name: 'login' })
      return
    }
    error.value = "Couldn't load the course."
  } finally {
    loading.value = false
  }
})

async function showAccessCode() {
  error.value = ''
  try {
    accessCode.value = (await getAccessCode(course.value.id)).access_code
  } catch (err) {
    error.value = err.detail ?? "Couldn't get the access code."
  }
}
</script>

<template>
  <section>
    <RouterLink :to="{ name: 'courses' }">&larr; All courses</RouterLink>

    <p v-if="loading">Loading...</p>

    <template v-else-if="course">
      <h2>{{ course.name }}</h2>
      <p>Language: {{ languageName }}</p>
      <p>You are {{ course.is_instructor ? 'an instructor' : 'a student' }} in this course.</p>

      <div v-if="course.is_instructor">
        <button type="button" @click="showAccessCode">Get access code</button>
        <p v-if="accessCode" class="access-code">
          Access code: <strong>{{ accessCode }}</strong> (share this with your students)
        </p>
      </div>
    </template>

    <p v-if="error">Error: {{ error }}</p>
  </section>
</template>
