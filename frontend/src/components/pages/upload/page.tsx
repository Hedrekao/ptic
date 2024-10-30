import React from 'react'
import { Panel } from 'app/components/panel/panel'
import { UploadArea } from './_components/upload-area'
import { buttonVariants, Button } from 'app/components/ui/button'
import { ChevronRight } from 'lucide-react'
import { UploadContextProvider } from 'app/components/pages/upload/_components/upload-context'
import { useShallowRouter } from 'app/components/shallow-router/useShallowRouter'

export const UploadPage = () => {
  const { navigate } = useShallowRouter()

  const goToSettingsPage = () => {
    navigate('settings')
  }

  return (
    <UploadContextProvider>
      <Panel>
        <h4 className="text-lg font-semibold tracking-tight">Upload files</h4>

        <UploadArea />

        <div className="w-full flex gap-3 justify-end">
          <Button onClick={goToSettingsPage} className={buttonVariants({ variant: 'default' })}>
            Next
            <ChevronRight size={16} />
          </Button>
        </div>
      </Panel>
    </UploadContextProvider>
  )
}

export default UploadPage
