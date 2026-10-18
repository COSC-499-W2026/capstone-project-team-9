/** Resolve with the device's {latitude, longitude}, or reject with the browser's error. */
export function getCurrentCoords() {
  return new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => resolve({ latitude: coords.latitude, longitude: coords.longitude }),
      reject,
    )
  })
}