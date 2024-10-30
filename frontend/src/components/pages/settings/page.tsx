'use client'

import React, { useState, useEffect } from 'react'
import { Panel } from 'app/components/panel/panel'
import { Button, buttonVariants } from 'app/components/ui/button'
import { ChevronRight } from 'lucide-react'
import { SettingOption, SettingOptionValue } from './_components/settings-option'
import { useShallowRouter } from 'app/components/shallow-router/shallow-router'
import { send, register } from 'app/services/websocket'
import { ERegisterEvent, TRegisterEvent } from 'app/services/types.register'
import { ESendEvent } from 'app/services/types.send'

const SettingsPage = () => {
  const [selectedMode, setSelectedMode] = useState<SettingOptionValue>('automatic')
  const { navigate } = useShallowRouter()

  useEffect(() => {
    register(ERegisterEvent.MODE_SELECTED, (data: TRegisterEvent['data']) => {
      console.log('Mode selected event received:', data)
    })
  }, [])

  const handleModeChange = (value: SettingOptionValue) => {
    setSelectedMode(value)
    console.log('Mode changed:', selectedMode)
  }

  const handleNextClick = () => {
    send({ type: ESendEvent.MODE_SELECTED, data: { mode: selectedMode } })
    console.log('Mode selected:', selectedMode)
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
          <p className="text-sm font-normal text-gray-500 mt-1">Classify images automatically</p>
        </SettingOption>

        <SettingOption
          value="semi-automatic"
          isSelected={selectedMode === 'semi-automatic'}
          onChange={handleModeChange}
        >
          Semi-automatic
          <p className="text-sm font-normal text-gray-500 mt-1">
            Classify images into 3 most likely categories and select the correct one
          </p>
        </SettingOption>

        <SettingOption value="manual" isSelected={selectedMode === 'manual'} onChange={handleModeChange}>
          Semi-automatic on demand
          <p className="text-sm font-normal text-gray-500 mt-1">
            Classify images and allow for manual selection when necessary
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
