/* @flow */

import React from 'react'

type Props = {|
    user: string,
    username: string,
    title: string,
    imageUrl: string,
|};

export default function UserImage(props: Props) {
    const { user, username, title, imageUrl } = props;

    if (!user) {
        return <img
            src='/static/img/anon.jpg'
            alt=''
            height='44'
            width='44'
        />;
    }

    return <div className='avatar'>
        <a
            href={ `/contributors/${username}` }
            title={ title }
            target='_blank'
            rel='noopener noreferrer'
            onClick={ (e: SyntheticMouseEvent<>) => e.stopPropagation() }
        >
            <img
                src={ imageUrl }
                alt=''
                height='44'
                width='44'
            />
        </a>
    </div>
}
