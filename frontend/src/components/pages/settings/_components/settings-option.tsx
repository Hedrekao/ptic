import React, { PropsWithChildren } from 'react'
import { Check } from 'lucide-react'

export type SettingOptionValue = 'automatic' | 'semi-automatic' | 'manual'
interface SettingOptionProps extends PropsWithChildren {
  value: SettingOptionValue
  isSelected: boolean
  onChange: (value: SettingOptionValue) => void
}

export const SettingOption = ({ value, isSelected, onChange, children }: SettingOptionProps) => {
  return (
    <div className={`flex flex-col p-4 rounded-lg ${isSelected ? 'bg-blue-50 border border-blue-200' : 'border'}`}>
      <label className="flex items-center gap-2 font-bold">
        <input type="radio" value={value} checked={isSelected} onChange={() => onChange(value)} className="hidden" />
        <div
          className={`w-5 h-5 rounded-full border-2 ${
            isSelected ? 'border-black bg-black' : 'border-gray-300'
          } flex items-center justify-center`}
        >
          {isSelected && <Check size={16} className="text-white" />}
        </div>
        <div>{children}</div>
      </label>
    </div>
  )
}
