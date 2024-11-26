"use client";

import React from "react";
import { UploadProgress } from "./upload-progress";
import { useUploadContext } from 'app/components/pages/upload/_components/upload-context'
import { FileInput } from 'lucide-react'

export const UploadArea = () => {
  const { onUpload, progress } = useUploadContext()


  console.log(progress)
  return (
    <div className="flex flex-col gap-2 w-full">
      <div className={`w-full border border-dashed border-slate-400 rounded-lg h-60 flex flex-col justify-center items-center gap-3`}>
        <input
          type="file"
          className="hidden"
          disabled={progress !== 0}
          id="file-input"
          {...{ mozdirectory: "", webkitdirectory: "" }}
          onChange={(e) => onUpload(e)}
        />
        <label htmlFor="file-input">
          <FileInput size={48} className="text-slate-400" />
        </label>
        <p className="text-sm font-medium">
          Click
          {' '}
          <button
            className="underline"
            onClick={() => document.getElementById("file-input")?.click()}
          >
            here
          </button>
          {' '}
          to choose files to upload
        </p>
      </div>

      <UploadProgress />
    </div>
  );
};
