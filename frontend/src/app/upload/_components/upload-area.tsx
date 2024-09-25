import React from 'react'
import {FileInput} from "lucide-react";

export const UploadArea= () => {
    return (
        <div className='flex flex-col gap-2 w-full'>
            <div className='w-full border border-dashed border-slate-400 rounded-lg h-60 flex flex-col justify-center items-center gap-3'>
                <FileInput size={48} className='text-slate-400'/>

                <p className='text-sm font-medium'>Drag and Drop files here or <button className='underline'>Choose files</button>.</p>
            </div>

            <div className='w-full flex justify-between text-xs text-slate-700'>
                <p>Supported formats: JPEG</p>
                <p>Maximum size: 25MB</p>
            </div>
        </div>
    )
}