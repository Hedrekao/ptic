import React from "react";
import { Folder, X } from "lucide-react";

interface UploadProgressProps {
  fileName: string;
  fileSize: number;
  progress: number;
}

export const UploadProgress = ({
  fileName,
  fileSize,
  progress,
}: UploadProgressProps) => {
  return (
    <div className="flex items-center justify-between p-3 bg-gray border border-gray-200 rounded-lg shadow-sm">
      <div className="flex items-center gap-3 flex-grow">
        <div className="bg-gray p-2 rounded-lg">
          <Folder className="text-black" size={24} />
        </div>
        <div className="flex flex-col w-full">
          <div className="flex justify-between text-sm font-medium text-gray-700">
            <span>{fileName}</span>
            <span>{(fileSize / (1024 * 1024)).toFixed(1)}MB</span>
          </div>
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
      </div>
      <button className="ml-4 text-gray-400 hover:text-gray-600">
        <X size={20} />
      </button>
    </div>
  );
};

export default UploadProgress;
