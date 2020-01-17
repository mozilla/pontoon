/* @flow */

import * as React from 'react';
import ReactTimeAgo from 'react-time-ago';
import { Localized } from '@fluent/react';

import './Comment.css';

import { UserAvatar } from 'core/user'

import type { TranslationComment } from 'core/api';
import type { UserState } from 'core/user';


type Props = {|
    comment: TranslationComment,
    user: UserState,
    isTranslator: boolean,
    deleteComment: (number) => void,
|};


export default function Comment(props: Props) {
    const { comment, user, isTranslator, deleteComment} = props;

    if (!comment) {
        return null;
    }

    // Does the currently logged in user own this Comment?
    const ownComment = (
        user && user.username &&
        user.username === comment.username
    );

    let canDelete = (isTranslator || ownComment);

    const _delete = (event: SyntheticMouseEvent<HTMLButtonElement>) => {
        event.stopPropagation();
        deleteComment(comment.id);
    }

    return <li className='comment'>
        <UserAvatar
            user={ comment.author }
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
                { !canDelete ? null :
                    <Localized id='comments-Comment--delete-button'>
                        <button
                            className='btn'
                            onClick={ _delete }
                        >
                            Delete
                        </button>
                    </Localized>
                }
            </div>
        </div>
    </li>
}
