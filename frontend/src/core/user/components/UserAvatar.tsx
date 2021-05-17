import * as React from 'react';
import { Localized } from '@fluent/react';

type Props = {
    username: string;
    title?: string;
    imageUrl: string;
};

export default function UserAvatar(props: Props): React.ReactElement<'div'> {
    const { username, title, imageUrl } = props;

    return (
        <div className='user-avatar'>
            <a
                href={`/contributors/${username}`}
                title={!title ? null : title}
                target='_blank'
                rel='noopener noreferrer'
                onClick={(e: React.MouseEvent) => e.stopPropagation()}
            >
                <Localized id='user-UserAvatar--alt-text' attrs={{ alt: true }}>
                    <img
                        src={imageUrl}
                        alt='User Profile'
                        height='44'
                        width='44'
                    />
                </Localized>
            </a>
        </div>
    );
}
