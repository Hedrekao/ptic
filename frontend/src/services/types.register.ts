export enum ERegisterEvent {
  UPLOAD_PROGRESS = 'upload_progress',
  MODE_SELECTED = 'mode_selected',
  PREDICTION_PROGRESS = 'prediction_progress',
  PREDICTION_APPROVAL_REQUEST = 'prediction_approval_request',
  CSV_FILE = 'csv_file',
}

export type TUploadProgressPayload = {
  progress: number
}

export type TModeSelectedPayload = {
  mode: string
}

export type TPredictionProgressPayload = {
  filesToPredict: number
  approvedFiles: number
}

export type TPredictionApprovalRequestPayload = {
  fileToApprove: {
    productName: string
    predictedClasses: {
      class: string
      weight: number
    }[]
    filePaths: string[]
  }
}

export type TCsvFilePayload = {
  csvData: string
}

export type TRegisterEvent =
  | {
      type: ERegisterEvent.UPLOAD_PROGRESS
      data: TUploadProgressPayload
    }
  | {
      type: ERegisterEvent.MODE_SELECTED
      data: TModeSelectedPayload
    }
  | {
      type: ERegisterEvent.PREDICTION_PROGRESS
      data: TPredictionProgressPayload
    }
  | {
      type: ERegisterEvent.PREDICTION_APPROVAL_REQUEST
      data: TPredictionApprovalRequestPayload
    }
  | {
      type: ERegisterEvent.CSV_FILE
      data: TCsvFilePayload
    }
