/* @flow */

import * as React from 'react';
import ReactTimeAgo from 'react-time-ago';
import { Localized } from '@fluent/react';

import './Comment.css';

import type { TranslationComment } from 'core/api';

import { UserAvatar } from 'core/user'


type Props = {|
    comment: TranslationComment,
|};


const deleteComment = () => {
    console.log('Delete')
}

const shareComment = () => {
    console.log('Share')
}

export default function Comment(props: Props) {
    const { comment } = props;

    if (!comment) {
        return null;
    }

    return <li className='comment'>
        <UserAvatar
            user={ comment.author }
            username={ comment.username }
            title=''
            imageUrl={ comment.userGravatarUrlSmall }
        />
        <div className='container'>
            <div className='content'>
                <a
                    href={ `/contributors/${comment.username}` }
                    target='_blank'
                    rel='noopener noreferrer'
                    onClick={ (e: SyntheticMouseEvent<>) => e.stopPropagation() }
                >
                    { comment.author }
                </a>
                <p>
                    { comment.content }
                </p>
            </div>
            <div className='info'>
                <ReactTimeAgo
                    dir='ltr'
                    date={ new Date(comment.dateIso) }
                    title={ `${comment.createdAt} UTC` }
                />
                { '\u2022' }
                <Localized
                id='comments-Comment--delete-button'
                attrs={{ title: true }}
                >
                    <button
                        title='Delete'
                        onClick={ deleteComment }
                    >
                        DELETE
                    </button>
                </Localized>
                { '\u2022' }
                <Localized
                id='comments-Comment--share-button'
                attrs={{ title: true }}
                >
                    <button
                        title='Share'
                        onClick={ shareComment }
                    >
                        SHARE
                    </button>
                </Localized>
            </div>
        </div>
    </li>
}
