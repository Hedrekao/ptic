import { WS_URL } from 'app/services/utils'
import { TSendEvent } from 'app/services/types.send'
import { ERegisterEvent, TRegisterEvent } from 'app/services/types.register'

export const socket = new WebSocket(WS_URL)

socket.onopen = () => console.log('Connected')
socket.onerror = (error) => console.error('WebSocket error:', error)
socket.onclose = (event) => console.log('Connection closed:', event.code, event.reason)

const REGISTERED_EVENTS: Record<ERegisterEvent, (payload: TRegisterEvent['data']) => void> = {
  [ERegisterEvent.UPLOAD_PROGRESS]: () => {},
  [ERegisterEvent.MODE_SELECTED]: () => {},
  [ERegisterEvent.PREDICTION_PROGRESS]: () => {},
  [ERegisterEvent.PREDICTION_APPROVAL_REQUEST]: () => {},
  [ERegisterEvent.CSV_FILE]: () => {},
}

export const register = (event: ERegisterEvent, callback: (payload: TRegisterEvent['data']) => void) => {
  REGISTERED_EVENTS[event] = callback
}

socket.onmessage = (event) => {
  const data = JSON.parse(event.data)
  const callback = REGISTERED_EVENTS[data.type as ERegisterEvent]
  callback(data.data)
}

export const send = (event: TSendEvent) => {
  socket.send(JSON.stringify(event))
}

