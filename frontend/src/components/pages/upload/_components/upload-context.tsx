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
  progress: number
}

const UploadContext = React.createContext<TUploadContext>({} as TUploadContext)

export const UploadContextProvider = (props: PropsWithChildren) => {
  const [progress, setProgress] = React.useState<number>(0)
  const [dirName, setDirName] = React.useState<string | null>(null)

  useEffect(() => {
    register(ERegisterEvent.UPLOAD_PROGRESS, (data: TRegisterEvent['data']) => {
      const uploadProgressData = data as TUploadProgressPayload
      console.log(uploadProgressData.progress)
      setProgress(uploadProgressData.progress)
    })
  }, [])

  const onUpload = (data: ChangeEvent<HTMLInputElement>) => {
    const files = data.target.files

    if (!files || files.length === 0) return

    const rootDir = files[0].webkitRelativePath.split('/')[0]
    setDirName(rootDir)

    send({
      type: ESendEvent.FILE_UPLOAD_INIT,
      data: {
        numberOfFiles: files.length,
        rootDir: rootDir
      }
    })

    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-expect-error
    for (const file of files) {
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

  return (
    <UploadContext.Provider value={{ dirName, onUpload, progress }}>
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
