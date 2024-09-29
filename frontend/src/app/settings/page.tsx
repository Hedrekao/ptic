"use client";

import React, { useState } from "react";
import { Panel } from "app/components/panel/panel";
import { Button, buttonVariants } from "app/components/ui/button";
import { ChevronRight } from "lucide-react";
import Link from "next/link";

interface SettingOptionProps {
  label: string;
  description: string;
  value: string;
  selectedValue: string;
  onChange: (value: string) => void;
}

const SettingOption = ({
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
      <label className="flex items-center gap-2 font-medium">
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

const SettingsPage = () => {
  const [selectedMode, setSelectedMode] = useState<string>("automatic");

  const handleModeChange = (value: string) => {
    setSelectedMode(value);
  };

  return (
    <Panel>
      <h2 className="text-xl font-semibold mb-6">Settings</h2>
      <div className="flex flex-col gap-4 mb-8">
        <SettingOption
          label="Automatic"
          description="Classify images automatically"
          value="automatic"
          selectedValue={selectedMode}
          onChange={handleModeChange}
        />
        <SettingOption
          label="Semi-automatic"
          description="Classify images into 3 most likely categories and select the correct one"
          value="semi-automatic"
          selectedValue={selectedMode}
          onChange={handleModeChange}
        />
        <SettingOption
          label="Semi-automatic on demand"
          description="Classify images and allow for manual selection when necessary"
          value="semi-automatic-on-demand"
          selectedValue={selectedMode}
          onChange={handleModeChange}
        />
      </div>
      <div className="flex justify-end gap-3">
        <Button variant="ghost">Cancel</Button>
        <Link
          href="/settings"
          className={buttonVariants({ variant: "default" })}
        >
          Next
          <ChevronRight size={16} />
        </Link>
      </div>
    </Panel>
  );
};

export default SettingsPage;
