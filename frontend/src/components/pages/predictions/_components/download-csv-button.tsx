import React, { useEffect, useState } from 'react'
import { usePredictions } from './predictions-context'
import { Button, buttonVariants } from 'app/components/ui/button'

export const DownloadCSVButton = () => {
  const { csvBlob } = usePredictions()
  const [blobUrl, setBlobUrl] = useState<string | null>(null)

  useEffect(() => {
    if (csvBlob) {
      const url = URL.createObjectURL(csvBlob)
      setBlobUrl(url)
      return () => URL.revokeObjectURL(url)
    }
  }, [csvBlob])

  return (
    <a href={blobUrl ?? undefined} download="predictions.csv">
      <Button disabled={!blobUrl} className={buttonVariants({ variant: 'default' })}>Download CSV</Button>
    </a>
  )
}
