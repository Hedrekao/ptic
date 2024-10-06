"use client";

import React, { useState } from "react";
import { FileInput } from "lucide-react";
import { UploadProgress } from "./upload-progress";

export const UploadArea = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
      setUploadProgress(0);
    }
  };

  const handleUpload = async () => {
    if (selectedFile) {
      console.log("Uploading file:", selectedFile.name);
      const formData = new FormData();
      formData.append("file", selectedFile);

      const xhr = new XMLHttpRequest();
      xhr.open("POST", "/upload");

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const progress = (event.loaded / event.total) * 100;
          setUploadProgress(progress);
        }
      };

      xhr.onload = () => {
        if (xhr.status === 200) {
          console.log("File uploaded successfully");
          setUploadProgress(100); // Set progress to 100% on success
        } else {
          console.error("Failed to upload file", xhr.statusText);
        }
      };

      xhr.onerror = () => {
        console.error("Error uploading file", xhr.statusText);
      };

      xhr.send(formData);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragEnter = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
  };

  const handleDragLeave = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
    if (event.dataTransfer.files && event.dataTransfer.files.length > 0) {
      setSelectedFile(event.dataTransfer.files[0]);
    }
  };

  return (
    <div className="flex flex-col gap-2 w-full">
      <div
        className={`w-full border border-dashed border-slate-400 rounded-lg h-60 flex flex-col justify-center items-center gap-3 ${
          isDragging ? "bg-gray-200" : ""
        }`}
        onDragOver={handleDragOver}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          onChange={handleFileChange}
          className="hidden"
          id="file-input"
        />
        <label htmlFor="file-input">
          <FileInput size={48} className="text-slate-400" />
        </label>
        <p className="text-sm font-medium">
          Drag and Drop files here or{" "}
          <button
            className="underline"
            onClick={() => document.getElementById("file-input")?.click()}
          >
            Choose files
          </button>
          .
        </p>
      </div>

      <div className="w-full flex justify-between text-xs text-slate-700">
        <p>Supported formats: JPEG</p>
        <p>Maximum size: 25MB</p>
      </div>

      {selectedFile && (
        <div className="w-full flex justify-between text-xs text-slate-700">
          <p>Selected file: {selectedFile.name}</p>
          <button onClick={handleUpload} className="underline">
            Upload
          </button>
        </div>
      )}

      {selectedFile && (
        <UploadProgress
          fileName={selectedFile.name}
          fileSize={selectedFile.size}
          progress={uploadProgress}
        />
      )}
    </div>
  );
};
