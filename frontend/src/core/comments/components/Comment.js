/* @flow */

import * as React from 'react';
import Linkify from 'react-linkify';
import parse from 'html-react-parser';
import ReactTimeAgo from 'react-time-ago';
import { Localized } from '@fluent/react';

import './Comment.css';

import { UserAvatar } from 'core/user';

import type { TranslationComment } from 'core/api';

type Props = {|
    comment: TranslationComment,
    canPin?: boolean,
    togglePinnedStatus?: (boolean, number) => void,
|};

export default function Comment(props: Props) {
    const { comment, canPin, togglePinnedStatus } = props;

    if (!comment) {
        return null;
    }

    const handlePinAndUnpin = () => {
        if (!togglePinnedStatus) {
            return;
        }
        togglePinnedStatus(!comment.pinned, comment.id);
    };

    return (
        <li className='comment'>
            <UserAvatar
                username={comment.username}
                imageUrl={comment.userGravatarUrlSmall}
            />
            <div className='container'>
                <div className='content'>
                    <div>
                        <a
                            className='comment-author'
                            href={`/contributors/${comment.username}`}
                            target='_blank'
                            rel='noopener noreferrer'
                            onClick={(e: SyntheticMouseEvent<>) =>
                                e.stopPropagation()
                            }
                        >
                            {comment.author}
                        </a>
                        <Linkify
                            properties={{
                                target: '_blank',
                                rel: 'noopener noreferrer',
                            }}
                        >
                            {/* We can safely use parse with comment.content as it is
                             * sanitized when coming from the DB. See:
                             *   - pontoon.base.forms.AddCommentForm(}
                             *   - pontoon.base.forms.HtmlField()
                             */}
                            <span dir='auto'>{parse(comment.content)}</span>
                        </Linkify>
                        {!comment.pinned ? null : (
                            <div className='comment-pin'>
                                <div className='fa fa-thumbtack'></div>
                                <Localized id='comments-Comment--pinned'>
                                    <span className='pinned'>PINNED</span>
                                </Localized>
                            </div>
                        )}
                    </div>
                </div>
                <div className='info'>
                    <ReactTimeAgo
                        dir='ltr'
                        date={new Date(comment.dateIso)}
                        title={`${comment.createdAt} UTC`}
                    />
                    {canPin ? (
                        comment.pinned ? (
                            // Unpin Button
                            <Localized
                                id='comments-Comment--unpin-button'
                                attrs={{ title: true }}
                            >
                                <button
                                    className='pin-button'
                                    title='Unpin comment'
                                    onClick={handlePinAndUnpin}
                                >
                                    {'UNPIN'}
                                </button>
                            </Localized>
                        ) : (
                            // Pin Button
                            <Localized
                                id='comments-Comment--pin-button'
                                attrs={{ title: true }}
                            >
                                <button
                                    className='pin-button'
                                    title='Pin comment'
                                    onClick={handlePinAndUnpin}
                                >
                                    {'PIN'}
                                </button>
                            </Localized>
                        )
                    ) : null}
                </div>
            </div>
        </li>
    );
}
