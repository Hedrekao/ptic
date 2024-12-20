import { SettingOptionValue } from 'app/components/pages/settings/_components/settings-option'

export enum ESendEvent {
  FILE_UPLOAD_INIT = 'init_upload',
  FILE_UPLOAD = 'file_upload',
  MODE_SELECTED = 'select_mode',
  INIT_PREDICTIONS = 'init_predictions',
  PREDICTION_APPROVAL = 'prediction_approval',
  CANCEL_UPLOAD = 'cancel_upload',
}

type TFileUploadInitPayload = {
  numberOfFiles: number
  rootDir: string
  uploadId: number
}

type TFileUploadPayload = {
  fileName: string
  fileData: string
}

type TModeSelectedPayload = {
  mode: SettingOptionValue
}

type TPredictionApprovalPayload = {
  productName: string
  class: string
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
  | {
      type: ESendEvent.INIT_PREDICTIONS
    }
  | {
      type: ESendEvent.PREDICTION_APPROVAL
      data: TPredictionApprovalPayload
    }
  | {
      type: ESendEvent.CANCEL_UPLOAD
    }
