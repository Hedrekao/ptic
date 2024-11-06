import React from 'react'
import { Panel } from 'app/components/panel/panel'
import { UploadArea } from './_components/upload-area'
import { buttonVariants, Button } from 'app/components/ui/button'
import { ChevronRight } from 'lucide-react'
import { useUploadContext } from 'app/components/pages/upload/_components/upload-context'
import { useShallowRouter } from 'app/components/shallow-router'

export const UploadPage = () => {
  const {progress} = useUploadContext()
  const { navigate } = useShallowRouter()

  const goToSettingsPage = () => {
    navigate('settings')
  }

  return (
      <Panel>
        <h4 className="text-lg font-semibold tracking-tight">Upload files</h4>

        <UploadArea />

        <div className="w-full flex gap-3 justify-end">
          <Button onClick={goToSettingsPage} className={buttonVariants({ variant: 'default' })} disabled={progress !== 100}>
            Next
            <ChevronRight size={16} />
          </Button>
        </div>
      </Panel>
  )
}

export default UploadPage
