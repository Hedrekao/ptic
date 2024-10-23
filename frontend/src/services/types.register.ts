
export enum ERegisterEvent {
  UPLOAD_PROGRESS = 'upload_progress',
  MODE_SELECTED = 'mode_selected',
}

export type TUploadProgressPayload = {
  progress: number
}

export type TModeSelectedPayload = {
  mode: string
}

export type TRegisterEvent = {
  type: ERegisterEvent.UPLOAD_PROGRESS
  data: TUploadProgressPayload
} | {
  type: ERegisterEvent.MODE_SELECTED
  data: TModeSelectedPayload
}




