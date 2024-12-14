'use client'

import React, { useState, useEffect } from 'react'
import { Panel } from 'app/components/panel/panel'
import { Button, buttonVariants } from 'app/components/ui/button'
import { ChevronRight } from 'lucide-react'
import { SettingOption, SettingOptionValue } from './_components/settings-option'
import { useShallowRouter } from 'app/components/shallow-router'
import { send } from 'app/services/websocket'
import { ESendEvent } from 'app/services/types.send'

const SettingsPage = () => {
  const [selectedMode, setSelectedMode] = useState<SettingOptionValue>('automatic')
  const { navigate } = useShallowRouter()

  useEffect(() => {
    send({
      type: ESendEvent.MODE_SELECTED,
      data: { mode: selectedMode },
    })
  }, [selectedMode])

  const handleModeChange = (value: SettingOptionValue) => {
    setSelectedMode(value)
  }

  const handleNextClick = () => {
    send({ type: ESendEvent.INIT_PREDICTIONS })
    navigate('predictions')

  }

  const goToUploadPage = () => {
    navigate('upload')
  }

  return (
    <Panel>
      <h2 className="text-xl font-semibold mb-4">Settings</h2>
      <div className="flex flex-col gap-4 mb-4">
        <SettingOption value="automatic" isSelected={selectedMode === 'automatic'} onChange={handleModeChange}>
          Automatic
          <p className="text-sm font-normal text-gray-500 mt-1">Classify products automatically</p>
        </SettingOption>

        <SettingOption
          value="semi-automatic"
          isSelected={selectedMode === 'semi-automatic'}
          onChange={handleModeChange}
        >
          Semi-automatic
          <p className="text-sm font-normal text-gray-500 mt-1">
            Allow the model to automatically classify products when confident, otherwise select the correct category from a list of 5 most likely categories
          </p>
        </SettingOption>

        <SettingOption value="manual" isSelected={selectedMode === 'manual'} onChange={handleModeChange}>
          Manual
          <p className="text-sm font-normal text-gray-500 mt-1">
            Manually classify products into the correct category from a list of 5 most likely categories
          </p>
        </SettingOption>
      </div>
      <div className="flex justify-end gap-3">
        <Button onClick={goToUploadPage} className={buttonVariants({ variant: 'ghost' })}>
          Cancel
        </Button>
        <Button onClick={handleNextClick} className={buttonVariants({ variant: 'default' })}>
          Next
          <ChevronRight size={16} />
        </Button>
      </div>
    </Panel>
  )
}

export default SettingsPage
