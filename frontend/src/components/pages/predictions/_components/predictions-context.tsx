import React, { PropsWithChildren, useEffect } from 'react'
import {
  ERegisterEvent, TCsvFilePayload,
  TPredictionApprovalRequestPayload,
  TPredictionProgressPayload,
  TRegisterEvent,
} from 'app/services/types.register'
import { register, send } from 'app/services/websocket'
import { ESendEvent } from 'app/services/types.send'

interface TPredictionsContext {
  approvedFiles: number
  allFiles: number
  progress: number
  approvalRequest: TPredictionApprovalRequestPayload['fileToApprove'] | null
  onApprove: (className: string) => void
  csvBlob: Blob | null
}

const PredictionsContext = React.createContext<TPredictionsContext>({} as TPredictionsContext)

export const PredictionsContextProvider = (props: PropsWithChildren) => {
  const [approvedFiles, setApprovedFiles] = React.useState<number>(0)
  const [allFiles, setAllFiles] = React.useState<number>(0)
  const [approvalRequest, setApprovalRequest] = React.useState<TPredictionsContext['approvalRequest']>(null)
  const [csvBlob, setCsvBlob] = React.useState<Blob | null>(null)

  const onApprove = (className: string) => {
    if (!approvalRequest) return

    send({
      type: ESendEvent.PREDICTION_APPROVAL,
      data: {
        productName: approvalRequest?.productName,
        class: className
      }
    })

    setApprovalRequest(null)
  }

  useEffect(() => {
    register(ERegisterEvent.PREDICTION_APPROVAL_REQUEST, (data: TRegisterEvent['data']) => {
      const approvalRequestData = data as TPredictionApprovalRequestPayload
      setApprovalRequest(approvalRequestData.fileToApprove)
    })

    register(ERegisterEvent.PREDICTION_PROGRESS, (data: TRegisterEvent['data']) => {
      const predictionProgressData = data as TPredictionProgressPayload
      setApprovedFiles(predictionProgressData.approvedFiles)
      setAllFiles(predictionProgressData.filesToPredict)
    })

    register(ERegisterEvent.CSV_FILE, (data: TRegisterEvent['data']) => {
      const csvData = data as TCsvFilePayload

      const blob = new Blob([csvData.csvData], { type: 'text/csv' })
      setCsvBlob(blob)
    })
  }, [])

  return (
    <PredictionsContext.Provider value={{
      approvedFiles,
      allFiles,
      progress: approvedFiles / allFiles * 100,
      approvalRequest,
      onApprove,
      csvBlob
    }}>
      {props.children}
    </PredictionsContext.Provider>
  )
}

export const usePredictions = () => {
  const context = React.useContext(PredictionsContext)

  if (!context) {
    throw new Error('usePredictions must be used within a PredictionsContextProvider')
  }

  return context
}
