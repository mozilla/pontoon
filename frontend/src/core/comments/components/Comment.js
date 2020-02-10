/* @flow */

import * as React from 'react';
import ReactTimeAgo from 'react-time-ago';

import './Comment.css';

import { UserAvatar } from 'core/user'

import type { TranslationComment } from 'core/api';


type Props = {|
    comment: TranslationComment,
|};


export default function Comment(props: Props) {
    const { comment } = props;

    if (!comment) {
        return null;
    }

    return <li className='comment'>
        <UserAvatar
            username={ comment.username }
            imageUrl={ comment.userGravatarUrlSmall }
        />
        <div className='container'>
            <div className='content' dir='auto'>
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
            </div>
        </div>
    </li>
}
