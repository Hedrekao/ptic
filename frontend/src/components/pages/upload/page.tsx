import React from 'react'
import {Panel} from "app/components/panel/panel";
import {UploadArea} from "./_components/upload-area";
import {buttonVariants} from "app/components/ui/button";
import {ChevronRight} from "lucide-react";
import Link from "next/link";
import { UploadContextProvider } from 'app/components/pages/upload/_components/upload-context'

export const UploadPage = () => {
    return (
      <UploadContextProvider>
        <Panel>
            <h4 className='text-lg font-semibold tracking-tight'>Upload files</h4>

            <UploadArea />

            <div className='w-full flex gap-3 justify-end'>
                <Link href={'/settings'} className={buttonVariants({ variant: "default" })}>
                    Next
                    <ChevronRight size={16} />
                </Link>
            </div>
        </Panel>
      </UploadContextProvider>
    )
}

export default UploadPage