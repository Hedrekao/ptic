import React from 'react'
import { usePredictions } from 'app/components/pages/predictions/_components/predictions-context'
import { RadioGroup, RadioGroupItem } from 'app/components/ui/radio-group'
import { Label } from 'app/components/ui/label'
import { Button } from 'app/components/ui/button'
import { ImageGrid } from './image-grid'

export const ApprovalBlock = () => {
  const { approvalRequest, onApprove } = usePredictions()
  const [selectedClass, setSelectedClass] = React.useState<string | null>(null)

  React.useEffect(() => {
    if (approvalRequest?.predictedClasses.length) {
      setSelectedClass(approvalRequest.predictedClasses[0].class)
    }
  }, [approvalRequest])

  const onSelectOption = (value: string) => {
    setSelectedClass(value)
  }

  const approve = () => {
    if (!selectedClass) return

    onApprove(selectedClass)
    setSelectedClass(null)
  }

  if (!approvalRequest) return null

  return (
    <div className={'w-full flex gap-4 items-center justify-around'}>
      <ImageGrid filePaths={approvalRequest.filePaths} />
      <div className={'flex flex-col gap-2'}>
        <RadioGroup onValueChange={onSelectOption} value={selectedClass || ''}>
          {approvalRequest.predictedClasses.map((predictedClass) => (
            <div className="flex items-center space-x-2" key={predictedClass.class}>
              <RadioGroupItem value={predictedClass.class} id={predictedClass.class} />
              <Label htmlFor={predictedClass.class}>
                {predictedClass.class} ({(predictedClass.weight * 100).toFixed(3)}%)
              </Label>
            </div>
          ))}
        </RadioGroup>
        <Button onClick={approve} className={'bg-blue-500 text-white'}>
          Select
        </Button>
      </div>
    </div>
  )
}
