import React from 'react'
import { usePredictions } from 'app/components/pages/predictions/_components/predictions-context'
import { RadioGroup, RadioGroupItem } from 'app/components/ui/radio-group'
import { Label } from 'app/components/ui/label'
import { Button } from 'app/components/ui/button'
import Image from 'next/image'

export const ApprovalBlock= () => {
  const {approvalRequest, onApprove} = usePredictions()
  const [selectedClass, setSelectedClass] = React.useState<string | null>(null)

  const onSelectOption = (value: string) => {
    setSelectedClass(value)
  }

  const approve = () => {
    if(!selectedClass) return

    onApprove(selectedClass)
  }

  if(!approvalRequest) return null

  return (
    <div className={'w-full flex gap-3'}>
      <Image src={`http://localhost:4200/uploads/${approvalRequest.fileName}`} alt={'file to manually classify'} width={300} height={300}/>
      <div className={'flex flex-col gap-2'}>
          <RadioGroup onValueChange={onSelectOption}>
            {approvalRequest.predictedClasses.map(predictedClass => (
              <div className="flex items-center space-x-2" key={predictedClass.class}>
                <RadioGroupItem value={predictedClass.class} id={predictedClass.class} />
                <Label htmlFor={predictedClass.class}>{predictedClass.class} ({predictedClass.weight * 100}%)</Label>
              </div>
              ))}
          </RadioGroup>
        <Button onClick={approve} className={'bg-blue-500 text-white'}>Select</Button>
      </div>
    </div>
  )
}