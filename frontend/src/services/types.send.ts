export enum ESendEvent {
  FILE_UPLOAD_INIT = 'init_upload',
  FILE_UPLOAD = 'file_upload',
  MODE_SELECTED = 'mode_selected',
}

type TFileUploadInitPayload = {
  numberOfFiles: number
}

type TFileUploadPayload = {
  fileName: string
  fileData: string
}

type TModeSelectedPayload = {
  mode: string
}

export type TSendEvent =
  | {
      type: ESendEvent.FILE_UPLOAD_INIT
      data: TFileUploadInitPayload
    }
  | {
      type: ESendEvent.FILE_UPLOAD
      data: TFileUploadPayload
    }
  | {
      type: ESendEvent.MODE_SELECTED
      data: TModeSelectedPayload
    }
