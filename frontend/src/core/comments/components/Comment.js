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
                <p>
                    <a
                        className='comment-author'
                        href={ `/contributors/${comment.username}` }
                        target='_blank'
                        rel='noopener noreferrer'
                        onClick={ (e: SyntheticMouseEvent<>) => e.stopPropagation() }
                    >
                        { comment.author }
                    </a>
                    {/* We can safely use comment.content because it is validated by
                    bleach before being saved into the database. */}
                    <span className='comment-content' dangerouslySetInnerHTML={ { __html: comment.content } } />
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
