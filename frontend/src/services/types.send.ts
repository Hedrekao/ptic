export enum ESendEvent {
  FILE_UPLOAD_INIT = 'init_upload',
  FILE_UPLOAD = 'file_upload'
}

type TFileUploadInitPayload = {
  numberOfFiles: number
}

type TFileUploadPayload = {
  fileName: string
  fileData: string
}

export type TSendEvent = |
  {
    type: ESendEvent.FILE_UPLOAD_INIT
    data: TFileUploadInitPayload
  } | {
    type: ESendEvent.FILE_UPLOAD
    data: TFileUploadPayload
  }