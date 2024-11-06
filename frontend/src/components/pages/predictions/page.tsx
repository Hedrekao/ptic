import React, { useMemo } from 'react'
import { Panel } from 'app/components/panel/panel'
import { usePredictions } from './_components/predictions-context'
import { ApprovalBlock } from './_components/approval-block'
import { DownloadCSVButton } from 'app/components/pages/predictions/_components/download-csv-button'

export const PredictionsPage= () => {
  const {approvedFiles, progress, allFiles} = usePredictions()

  if(allFiles === 0) <Panel>Loading</Panel>

  const progressLabel = useMemo(() => {
    if(allFiles === 0) return ''

    return `Completed ${approvedFiles} out of ${allFiles} (${progress}%)`
  }, [approvedFiles, allFiles, progress])

  return (
    <Panel>
      <div className="w-full flex flex-col gap-2 items-center">
        <h2 className="text-lg font-semibold tracking-tight">Classification in progress</h2>
        <p className="text-sm text-slate-700">{progressLabel}</p>
        <div className="w-3/4">
          <div className="w-full bg-blue-500 h-1.5 rounded-full" style={{ width: `${progress}%` }} />
        </div>
      </div>

      <ApprovalBlock />

      <div className="w-full flex gap-3 justify-end">
        <DownloadCSVButton />
      </div>
    </Panel>
)

}