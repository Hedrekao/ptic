export const WS_URL = "ws://localhost:4200/ws";

export const arrayBufferToBase64 = (buffer: ArrayBufferLike) =>  {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);  // Encode binary string as Base64
}