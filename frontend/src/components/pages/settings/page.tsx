"use client";

import React, { useState } from "react";
import { Panel } from "app/components/panel/panel";
import { Button, buttonVariants } from "app/components/ui/button";
import { ChevronRight } from "lucide-react";
import Link from "next/link";
import {
  SettingOption,
  SettingOptionValue,
} from "./_components/settings-option";

const SettingsPage = () => {
  const [selectedMode, setSelectedMode] =
    useState<SettingOptionValue>("automatic");

  const handleModeChange = (value: SettingOptionValue) => {
    setSelectedMode(value);
  };

  return (
    <Panel>
      <h2 className="text-xl font-semibold mb-4">Settings</h2>
      <div className="flex flex-col gap-4 mb-4">
        <SettingOption
          value="automatic"
          isSelected={selectedMode === "automatic"}
          onChange={handleModeChange}
        >
          Automatic
          <p className="text-sm font-normal text-gray-500 mt-1">
            Classify images automatically
          </p>
        </SettingOption>

        <SettingOption
          value="semi-automatic"
          isSelected={selectedMode === "semi-automatic"}
          onChange={handleModeChange}
        >
          Semi-automatic
          <p className="text-sm font-normal text-gray-500 mt-1">
            Classify images into 3 most likely categories and select the correct
            one
          </p>
        </SettingOption>

        <SettingOption
          value="semi-automatic-on-demand"
          isSelected={selectedMode === "semi-automatic-on-demand"}
          onChange={handleModeChange}
        >
          Semi-automatic on demand
          <p className="text-sm font-normal text-gray-500 mt-1">
            Classify images and allow for manual selection when necessary
          </p>
        </SettingOption>
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
