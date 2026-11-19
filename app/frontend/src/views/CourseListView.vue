<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { createCourse, enrollInCourse, getCurrentUser, getMyCourses } from '../api/course'
import { getLanguages } from '../api/game'

const COURSE_CREATOR_ROLES = ['instructor', 'admin']

const router = useRouter()

const user = ref(null)
const courses = ref([])
const languages = ref([])
const loading = ref(true)
const error = ref('')

// Create course form (teachers)
const showCreateForm = ref(false)
const courseName = ref('')
const languageId = ref(null)
const creating = ref(false)

// Enroll form (students)
const accessCode = ref('')
const enrolling = ref(false)

const isTeacher = computed(() => COURSE_CREATOR_ROLES.includes(user.value?.role))
const languageNames = computed(() => Object.fromEntries(languages.value.map((l) => [l.id, l.name])))

onMounted(async () => {
  try {
    const [me, myCourses, langs] = await Promise.all([getCurrentUser(), getMyCourses(), getLanguages()])
    user.value = me
    courses.value = myCourses
    languages.value = langs
    languageId.value = langs[0]?.id ?? null
  } catch (err) {
    if (err.status === 401) {
      await router.push({ name: 'login' })
      return
    }
    error.value = "Couldn't load your courses."
  } finally {
    loading.value = false
  }
})

function openCourse(course) {
  return router.push({ name: 'course', params: { courseId: course.id } })
}

async function submitCreate() {
  error.value = ''
  creating.value = true
  try {
    const course = await createCourse({ name: courseName.value.trim(), languageId: languageId.value })
    await openCourse(course)
  } catch (err) {
    error.value = err.detail ?? "Couldn't create the course."
  } finally {
    creating.value = false
  }
}

async function submitEnroll() {
  error.value = ''
  enrolling.value = true
  try {
    const course = await enrollInCourse(accessCode.value.trim())
    await openCourse(course)
  } catch (err) {
    error.value = err.detail ?? "Couldn't join the course."
  } finally {
    enrolling.value = false
  }
}
</script>

<template>
  <section>
    <h2>My Courses</h2>

    <p v-if="loading">Loading...</p>

    <template v-else-if="user">
      <div v-if="isTeacher">
        <button v-if="!showCreateForm" type="button" @click="showCreateForm = true">Create course</button>

        <form v-else class="create-course" @submit.prevent="submitCreate">
          <div>
            <label for="course-name">Course name: </label>
            <input id="course-name" v-model="courseName" maxlength="100" required />
          </div>
          <div>
            <label for="course-language">Language: </label>
            <select id="course-language" v-model="languageId" required>
              <option v-for="language in languages" :key="language.id" :value="language.id">
                {{ language.name }}
              </option>
            </select>
          </div>
          <button type="submit" :disabled="creating || !courseName.trim() || languageId == null">Create</button>
          <button type="button" @click="showCreateForm = false">Cancel</button>
        </form>
      </div>

      <form v-else class="enroll" @submit.prevent="submitEnroll">
        <label for="access-code">Join a course with an access code: </label>
        <input id="access-code" v-model="accessCode" maxlength="6" placeholder="ABC123" required />
        <button type="submit" :disabled="enrolling || accessCode.trim().length !== 6">Enroll</button>
      </form>

      <p v-if="!courses.length">You're not in any courses yet.</p>
      <ul v-else class="course-list">
        <li v-for="course in courses" :key="course.id">
          <RouterLink :to="{ name: 'course', params: { courseId: course.id } }">{{ course.name }}</RouterLink>
          ({{ languageNames[course.language_id] ?? 'Unknown language' }})
          <span v-if="course.is_instructor"> · Instructor</span>
        </li>
      </ul>
    </template>

    <p v-if="error">Error: {{ error }}</p>
  </section>
</template>
