/* @flow */

import React from 'react'
import { Localized } from '@fluent/react';

type Props = {|
    user: string,
    username: string,
    title: string,
    imageUrl: string,
|};

export default function UserAvatar(props: Props) {
    const { user, username, title, imageUrl } = props;

    if (!user) {
        return <Localized id='user-avatar-anonymous' attrs={{ title: true }} >
            <div className='user-avatar'>
                <img
                    src='/static/img/anon.jpg'
                    alt='Anonymous User'
                    height='44'
                    width='44'
                />
            </div>;
        </Localized>
    }

    return <Localized id='user-avatar' attrs={{ title: true }} >
        <div className='user-avatar'>
            <a
                href={ `/contributors/${username}` }
                title={ title }
                target='_blank'
                rel='noopener noreferrer'
                onClick={ (e: SyntheticMouseEvent<>) => e.stopPropagation() }
            >
                <img
                    src={ imageUrl }
                    alt='User Profile'
                    height='44'
                    width='44'
                />
            </a>
        </div>
    </Localized>
}
