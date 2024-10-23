import React, {PropsWithChildren} from 'react'

export const Panel = (props: PropsWithChildren) => {
    const {children} = props

    return (
        <div className='w-[800px] p-8 rounded-xl flex flex-col gap-8 bg-white mx-auto shadow-xl'>{children}</div>
    )
}