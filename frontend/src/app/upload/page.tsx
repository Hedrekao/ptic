import React from 'react'
import {Panel} from "app/components/panel/panel";
import {UploadArea} from "./_components/upload-area";
import {Button, buttonVariants} from "app/components/ui/button";
import {ChevronRight} from "lucide-react";
import Link from "next/link";

export const Page = () => {
    return (
        <Panel>
            <h4 className='text-lg font-semibold tracking-tight'>Upload files</h4>

            <UploadArea />

            <div className='w-full flex gap-3 justify-end'>
                <Button variant='ghost'>Cancel</Button>

                <Link href={'/settings'} className={buttonVariants({ variant: "default" })}>
                    Next
                    <ChevronRight size={16} />
                </Link>
            </div>
        </Panel>
    )
}

export default Page