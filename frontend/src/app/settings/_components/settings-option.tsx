import React from "react";

interface SettingOptionProps {
  label: string;
  description: string;
  value: string;
  selectedValue: string;
  onChange: (value: string) => void;
}

export const SettingOption = ({
  label,
  description,
  value,
  selectedValue,
  onChange,
}: SettingOptionProps) => {
  const isSelected = selectedValue === value;
  return (
    <div
      className={`flex flex-col p-4 rounded-lg ${
        isSelected ? "bg-blue-50 border border-blue-200" : "border"
      }`}
    >
      <label className="flex items-center gap-2 font-bold">
        <input
          type="radio"
          value={value}
          checked={isSelected}
          onChange={() => onChange(value)}
          className="hidden"
        />
        <div
          className={`w-5 h-5 rounded-full border-2 ${
            isSelected ? "border-blue-500 bg-blue-500" : "border-gray-300"
          } flex items-center justify-center`}
        >
          {isSelected && <div className="w-2 h-2 rounded-full bg-white" />}
        </div>
        {label}
      </label>
      <p className="text-sm text-gray-500 mt-1">{description}</p>
    </div>
  );
};
