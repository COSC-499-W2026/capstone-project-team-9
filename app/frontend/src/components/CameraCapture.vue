<script setup>
import { onBeforeUnmount, ref, watch } from 'vue'

/**
 * Take a photo with the device camera (live viewfinder, no gallery uploads).
 * v-model is the captured photo as a JPEG Blob, or null.
 */
const model = defineModel({ default: null })

const video = ref(null)
const status = ref('idle') // idle | starting | live | captured
const error = ref('')
const previewUrl = ref('')
let stream = null

function stopCamera() {
  stream?.getTracks().forEach((track) => track.stop())
  stream = null
}

function cameraErrorMessage(err) {
  switch (err?.name) {
    case 'NotAllowedError':
      return 'Camera access was blocked. Allow it in your browser settings and try again.'
    case 'NotFoundError':
    case 'OverconstrainedError':
      return 'No camera was found on this device.'
    case 'NotReadableError':
      return 'Your camera is being used by another app.'
    default:
      return "Couldn't start the camera."
  }
}

async function openCamera() {
  error.value = ''
  if (!navigator.mediaDevices?.getUserMedia) {
    // Browsers only allow the camera on https (or localhost)
    error.value = 'The camera needs a secure (https) connection.'
    return
  }
  status.value = 'starting'
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: 'environment' }, width: { ideal: 1920 }, height: { ideal: 1080 } },
      audio: false,
    })
    video.value.srcObject = stream // status becomes 'live' once the video has loaded
  } catch (err) {
    stopCamera()
    status.value = 'idle'
    error.value = cameraErrorMessage(err)
  }
}

async function capture() {
  const el = video.value
  if (!el?.videoWidth) return // no frame yet

  const canvas = document.createElement('canvas')
  canvas.width = el.videoWidth
  canvas.height = el.videoHeight
  canvas.getContext('2d').drawImage(el, 0, 0)
  const photo = await new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', 0.9))
  if (!photo) {
    error.value = "Couldn't take the photo. Try again."
    return
  }
  stopCamera()
  model.value = photo
}

function retake() {
  model.value = null
  openCamera()
}

function revokePreview() {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = ''
}

watch(model, (photo) => {
  revokePreview()
  if (photo) {
    previewUrl.value = URL.createObjectURL(photo)
    status.value = 'captured'
  } else if (status.value === 'captured') {
    status.value = 'idle' // parent cleared the photo, e.g. after a wrong answer
  }
})

onBeforeUnmount(() => {
  stopCamera()
  revokePreview()
})
</script>

<template>
  <div class="camera">
    <!-- Live viewfinder -->
    <div v-show="status === 'starting' || status === 'live'" class="camera__viewfinder">
      <video ref="video" autoplay muted playsinline @loadedmetadata="status = 'live'" />
      <div class="camera__frame" aria-hidden="true" />
      <span v-if="status === 'starting'" class="spinner camera__spinner" aria-label="Starting camera" />
      <button
        type="button"
        class="camera__shutter"
        :disabled="status !== 'live'"
        aria-label="Take photo"
        @click="capture"
      />
    </div>

    <!-- Captured photo -->
    <div v-if="status === 'captured'" class="camera__preview">
      <img :src="previewUrl" alt="Your photo" />
      <button type="button" class="camera__retake" @click="retake">Retake</button>
    </div>

    <!-- Not started -->
    <button v-if="status === 'idle'" type="button" class="camera__open" @click="openCamera">
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path
          d="M9.4 4.5 8.2 6.2H5.5A2.5 2.5 0 0 0 3 8.7v9.1a2.5 2.5 0 0 0 2.5 2.5h13a2.5 2.5 0 0 0 2.5-2.5V8.7a2.5 2.5 0 0 0-2.5-2.5h-2.7l-1.2-1.7a1.5 1.5 0 0 0-1.2-.6h-2.8a1.5 1.5 0 0 0-1.2.6Z"
        />
        <circle cx="12" cy="13" r="3.6" />
      </svg>
      <span class="camera__title">Take a photo</span>
      <span class="camera__hint">Point your camera at the room sign</span>
    </button>

    <p v-if="error" class="camera__error" role="alert">{{ error }}</p>
  </div>
</template>

<style scoped>
.camera {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

/* ---------- Viewfinder ---------- */
.camera__viewfinder,
.camera__preview {
  position: relative;
  overflow: hidden;
  aspect-ratio: 3 / 4;
  border-radius: var(--radius);
  background: #000;
  animation: pop-in 0.4s var(--ease);
}

.camera__viewfinder video,
.camera__preview img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Guide box for the sign, with the rest of the frame dimmed */
.camera__frame {
  position: absolute;
  inset: 28% 12%;
  border: 2px solid rgba(255, 255, 255, 0.85);
  border-radius: 16px;
  box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.3);
  pointer-events: none;
}

.camera__spinner {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 2rem;
  height: 2rem;
  margin: -1rem 0 0 -1rem;
  color: #fff;
}

/* iOS-style shutter: white disc inside a ring */
.camera__shutter {
  position: absolute;
  bottom: 1.25rem;
  left: 50%;
  width: 4.25rem;
  height: 4.25rem;
  margin-left: -2.125rem;
  border: 4px solid #fff;
  border-radius: 50%;
  background: transparent;
  transition: transform 0.15s var(--ease);
}

.camera__shutter::after {
  content: '';
  position: absolute;
  inset: 3px;
  border-radius: 50%;
  background: #fff;
}

.camera__shutter:active:not(:disabled) {
  transform: scale(0.9);
}

.camera__shutter:disabled {
  opacity: 0.4;
}

/* ---------- Captured photo ---------- */
.camera__retake {
  position: absolute;
  right: 0.75rem;
  bottom: 0.75rem;
  padding: 0.4rem 0.9rem;
  border: none;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  color: #fff;
  font-size: 0.8125rem;
  font-weight: 600;
}

/* ---------- Not started ---------- */
.camera__open {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
  width: 100%;
  padding: 2rem 1rem;
  border: 1.5px dashed var(--border);
  border-radius: var(--radius);
  background: var(--surface-sunken);
  transition:
    border-color 0.2s ease,
    background-color 0.2s ease;
}

.camera__open:hover {
  border-color: var(--accent);
  background: var(--accent-soft);
}

.camera__open svg {
  width: 2.25rem;
  height: 2.25rem;
  margin-bottom: 0.25rem;
  fill: none;
  stroke: var(--accent);
  stroke-width: 1.6;
  stroke-linejoin: round;
}

.camera__title {
  font-weight: 600;
}

.camera__hint {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.camera__error {
  margin: 0;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-sm);
  background: var(--danger-soft);
  color: var(--danger);
  font-size: 0.9375rem;
}

@keyframes pop-in {
  from {
    opacity: 0;
    transform: scale(0.96);
  }
}
</style>
