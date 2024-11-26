import React from "react";
import { Folder, X } from "lucide-react";
import { useUploadContext } from 'app/components/pages/upload/_components/upload-context'

export const UploadProgress = () => {
  const { dirName, progress, onUploadCancel } = useUploadContext()

  if (!dirName) return null

  return (
    <div className="flex items-center justify-between p-3 bg-gray border border-gray-200 rounded-lg shadow-sm">
      <div className="flex items-center gap-3 flex-grow">
        <div className="flex gap-2">
          <Folder className="text-black" size={24} />
          <span>{dirName}</span>
        </div>

        <div className="flex flex-col w-full mt-2">
          <div className="w-full bg-gray-200 rounded-full h-1.5 mt-2">
            <div
              className="bg-blue-500 h-1.5 rounded-full"
              style={{ width: `${progress}%` }}
            ></div>
          </div>

          <div className="text-right text-xs text-gray-500 mt-1">
            {progress.toFixed(0)}%
          </div>
        </div>
        <button onClick={onUploadCancel}>
          <X />
        </button>
      </div>
    </div>
  );
};

export default UploadProgress;
