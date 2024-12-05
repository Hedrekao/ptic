import React, { ChangeEvent, PropsWithChildren, useEffect } from 'react'
import { register, send } from 'app/services/websocket'
import { ESendEvent } from 'app/services/types.send'
import { arrayBufferToBase64 } from 'app/services/utils'
import {
  ERegisterEvent,
  TRegisterEvent,
  TUploadProgressPayload,
} from 'app/services/types.register'

interface TUploadContext {
  dirName: string | null
  onUpload: (e: ChangeEvent<HTMLInputElement>) => void
  onUploadCancel: () => void
  progress: number
}

const UploadContext = React.createContext<TUploadContext>({} as TUploadContext)

export const UploadContextProvider = (props: PropsWithChildren) => {
  const [progress, setProgress] = React.useState<number>(0)
  const [dirName, setDirName] = React.useState<string | null>(null)
  const [uploadId, setUploadId] = React.useState<number>(Date.now())

  useEffect(() => {
    register(ERegisterEvent.UPLOAD_PROGRESS, (data: TRegisterEvent['data']) => {
      const uploadProgressData = data as TUploadProgressPayload
      if (uploadId !== uploadProgressData.uploadId) return
      setProgress(uploadProgressData.progress)
    })
  }, [uploadId])

  const onUpload = (data: ChangeEvent<HTMLInputElement>) => {
    const files = data.target.files

    if (!files || files.length === 0) return

    // filter files based on extension
    const allowedExtensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']

    const filteredFiles = Array.from(files).filter((file) => {
      const extension = file.name.split('.').pop()
      return extension && allowedExtensions.includes(extension)
    })

    if (filteredFiles.length === 0) {
      return
    }

    const rootDir = filteredFiles[0].webkitRelativePath.split('/')[0]
    setDirName(rootDir)

    send({
      type: ESendEvent.FILE_UPLOAD_INIT,
      data: {
        numberOfFiles: filteredFiles.length,
        rootDir: rootDir,
        uploadId: uploadId
      }
    })

    for (const file of filteredFiles) {
      const reader = new FileReader();

      reader.onload = function(e) {
        if (!e.target || !e.target.result) return

        const fileData = e.target.result as ArrayBuffer;

        const base64Data = arrayBufferToBase64(fileData);

        send({
          type: ESendEvent.FILE_UPLOAD,
          data: {
            fileName: file.webkitRelativePath,
            fileData: base64Data
          }
        })
      };

      reader.readAsArrayBuffer(file);
    }
  }

  const onUploadCancel = () => {

    register(ERegisterEvent.UPLOAD_PROGRESS, () => { })
    send({
      type: ESendEvent.CANCEL_UPLOAD
    })

    setDirName(null)
    setProgress(0)
    setUploadId(Date.now())
  }

  return (
    <UploadContext.Provider value={{ dirName, onUpload, onUploadCancel, progress }}>
      {props.children}
    </UploadContext.Provider>
  )
}

export const useUploadContext = () => {
  const context = React.useContext(UploadContext)

  if (!context) {
    throw new Error('useUploadContext must be used within a UploadContextProvider')
  }

  return context
}
