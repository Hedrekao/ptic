"use client";

import React, { useState } from "react";
import { Panel } from "app/components/panel/panel";
import { Button, buttonVariants } from "app/components/ui/button";
import { ChevronRight } from "lucide-react";
import Link from "next/link";
import { SettingOption } from "./_components/settings-option";

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
