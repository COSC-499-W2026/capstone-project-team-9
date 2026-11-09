import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import CameraCapture from '@/components/CameraCapture.vue'

const PHOTO = new Blob(['jpeg'], { type: 'image/jpeg' })

let stopTrack
let getUserMedia

function stubCamera() {
  stopTrack = vi.fn()
  getUserMedia = vi.fn().mockResolvedValue({ getTracks: () => [{ stop: stopTrack }] })
  vi.stubGlobal('navigator', { ...navigator, mediaDevices: { getUserMedia } })
}

// jsdom has no camera or canvas: fake a loaded video frame and canvas.toBlob
function stubVideoFrame(wrapper) {
  const video = wrapper.find('video').element
  Object.defineProperty(video, 'videoWidth', { value: 1920, configurable: true })
  Object.defineProperty(video, 'videoHeight', { value: 1080, configurable: true })
}

async function openLiveCamera(wrapper) {
  await wrapper.find('.camera__open').trigger('click')
  await flushPromises()
  stubVideoFrame(wrapper)
  await wrapper.find('video').trigger('loadedmetadata')
}

beforeEach(() => {
  stubCamera()
  vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue({ drawImage: vi.fn() })
  vi.spyOn(HTMLCanvasElement.prototype, 'toBlob').mockImplementation((callback) => callback(PHOTO))
  URL.createObjectURL = vi.fn(() => 'blob:preview')
  URL.revokeObjectURL = vi.fn()
})

afterEach(() => {
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

describe('CameraCapture', () => {
  it('asks for the back camera when the player taps Take a photo', async () => {
    const wrapper = mount(CameraCapture)

    await wrapper.find('.camera__open').trigger('click')

    expect(getUserMedia).toHaveBeenCalledWith(
      expect.objectContaining({ video: expect.objectContaining({ facingMode: { ideal: 'environment' } }), audio: false }),
    )
  })

  it('has no way to upload a file', () => {
    const wrapper = mount(CameraCapture)

    expect(wrapper.find('input[type="file"]').exists()).toBe(false)
  })

  it('keeps the shutter disabled until the camera is live', async () => {
    const wrapper = mount(CameraCapture)
    await wrapper.find('.camera__open').trigger('click')
    await flushPromises()

    expect(wrapper.find('[aria-label="Take photo"]').attributes('disabled')).toBeDefined()

    await wrapper.find('video').trigger('loadedmetadata')

    expect(wrapper.find('[aria-label="Take photo"]').attributes('disabled')).toBeUndefined()
  })

  it('takes a JPEG photo, shows it and turns the camera off', async () => {
    const wrapper = mount(CameraCapture)
    await openLiveCamera(wrapper)

    await wrapper.find('[aria-label="Take photo"]').trigger('click')
    await flushPromises()

    expect(wrapper.emitted('update:modelValue').at(-1)).toEqual([PHOTO])
    expect(HTMLCanvasElement.prototype.toBlob).toHaveBeenCalledWith(expect.any(Function), 'image/jpeg', 0.9)
    expect(stopTrack).toHaveBeenCalled()
  })

  it('shows the photo with a Retake button that reopens the camera', async () => {
    const wrapper = mount(CameraCapture, { props: { modelValue: null } })
    await wrapper.setProps({ modelValue: PHOTO })

    expect(wrapper.find('img').attributes('src')).toBe('blob:preview')
    await wrapper.find('.camera__retake').trigger('click')

    expect(wrapper.emitted('update:modelValue').at(-1)).toEqual([null])
    expect(getUserMedia).toHaveBeenCalled()
  })

  it('explains when camera access is blocked', async () => {
    getUserMedia.mockRejectedValue(Object.assign(new Error('denied'), { name: 'NotAllowedError' }))
    const wrapper = mount(CameraCapture)

    await wrapper.find('.camera__open').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Camera access was blocked')
    expect(wrapper.find('.camera__open').exists()).toBe(true)
  })

  it('explains when the browser has no camera access (not https)', async () => {
    vi.stubGlobal('navigator', { ...navigator, mediaDevices: undefined })
    const wrapper = mount(CameraCapture)

    await wrapper.find('.camera__open').trigger('click')

    expect(wrapper.text()).toContain('secure (https) connection')
  })

  it('turns the camera off when it goes away', async () => {
    const wrapper = mount(CameraCapture)
    await openLiveCamera(wrapper)

    wrapper.unmount()

    expect(stopTrack).toHaveBeenCalled()
  })
})
