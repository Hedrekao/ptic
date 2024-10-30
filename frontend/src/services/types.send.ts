import { SettingOptionValue } from 'app/components/pages/settings/_components/settings-option'

export enum ESendEvent {
  FILE_UPLOAD_INIT = 'init_upload',
  FILE_UPLOAD = 'file_upload',
  MODE_SELECTED = 'select_mode',
}

type TFileUploadInitPayload = {
  numberOfFiles: number
}

type TFileUploadPayload = {
  fileName: string
  fileData: string
}

type TModeSelectedPayload = {
  mode: SettingOptionValue
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
