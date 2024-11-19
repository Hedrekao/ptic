export const serverUrl = process.env.NEXT_PUBLIC_SERVER_URL || 'http://localhost:4200'

const [protocol, host] = serverUrl.split('://')

export const WS_URL = `${protocol == 'https' ? 'wss' : 'ws'}://${host}/ws`

export const arrayBufferToBase64 = (buffer: ArrayBufferLike) => {
  let binary = ''
  const bytes = new Uint8Array(buffer)
  const len = bytes.byteLength
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i])
  }
  return window.btoa(binary) // Encode binary string as Base64
}
