'use client'

import React from "react";
import UploadPage from "app/components/pages/upload/page";
import SettingsPage from "app/components/pages/settings/page";

type TPath = 'upload' | 'settings'

const PATH_MAP = {
    upload: <UploadPage />,
    settings: <SettingsPage />
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