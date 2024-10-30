'use client'

import React, { useContext } from 'react'
import UploadPage from 'app/components/pages/upload/page'
import SettingsPage from 'app/components/pages/settings/page'
import { PredictionsPage } from 'app/components/pages/predictions/page'
import { UploadContextProvider } from 'app/components/pages/upload/_components/upload-context'
import { PredictionsContextProvider } from 'app/components/pages/predictions/_components/predictions-context'

type TPath = 'upload' | 'settings' | 'predictions'

const PATH_MAP = {
  upload: <UploadContextProvider><UploadPage /></UploadContextProvider>,
  settings: <SettingsPage />,
  predictions: <PredictionsContextProvider><PredictionsPage/></PredictionsContextProvider>,
}

interface TShallowRouterContext {
  currentPath: TPath
  navigate: (path: TPath) => void
}

export const ShallowRouterContext = React.createContext<TShallowRouterContext>({} as TShallowRouterContext)

export const ShallowRouter = () => {
  const [currentPath, setCurrentPath] = React.useState<TPath>('upload')

  const navigate = (path: TPath) => {
    setCurrentPath(path)
  }

  return (
    <ShallowRouterContext.Provider value={{ currentPath, navigate }}>
      {PATH_MAP[currentPath]}
    </ShallowRouterContext.Provider>
  )
}

export const useShallowRouter = () => {
  const context = useContext(ShallowRouterContext)
  if (!context) {
    throw new Error('useShallowRouter must be used within a ShallowRouterProvider')
  }
  return context
}
