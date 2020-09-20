/* @flow */

import * as React from 'react';
import Linkify from 'react-linkify';
import parse from 'html-react-parser';
import ReactTimeAgo from 'react-time-ago';
import { Localized } from '@fluent/react';

import './Comment.css';

import { UserAvatar } from 'core/user'

import type { TranslationComment } from 'core/api';

type Props = {|
    comment: TranslationComment,
    canPin?: boolean,
    updatePinnedComment?: (boolean, number) => void,
|};


export default function Comment(props: Props) {
    const { comment, canPin, updatePinnedComment } = props;

    if (!comment) {
        return null;
    }

    const handlePinnedComment = () => { 
        if (!updatePinnedComment) {
            return;
        }
        updatePinnedComment(!comment.pinned, comment.id)
    }

    return <li className='comment'>
        <UserAvatar
            username={ comment.username }
            imageUrl={ comment.userGravatarUrlSmall }
        />
        <div className='container'>
            <div className='content' dir='auto'>
                <div>
                    <a
                        className='comment-author'
                        href={ `/contributors/${comment.username}` }
                        target='_blank'
                        rel='noopener noreferrer'
                        onClick={ (e: SyntheticMouseEvent<>) => e.stopPropagation() }
                    >
                        { comment.author }
                    </a>
                    <Linkify properties={ { target: '_blank', rel: 'noopener noreferrer' } }>
                        {
                        /* We can safely use parse with comment.content as it is
                         * sanitized when coming from the DB. See:
                         *   - pontoon.base.forms.AddCommentsForm(}
                         *   - pontoon.base.forms.HtmlField()
                         */
                        }
                        { parse(comment.content) }
                    </Linkify>
                    { !comment.pinned ? null :
                        <div className="fa fa-thumbtack comment-pin"></div>
                    }
                </div>
            </div>
            <div className='info'>
                <ReactTimeAgo
                    dir='ltr'
                    date={ new Date(comment.dateIso) }
                    title={ `${comment.createdAt} UTC` }
                />
                { canPin ?
                    <Localized
                        id="comments-Comment--pin-button"
                        attrs={{ title: true }}
                        vars={{
                            pinnedTitle: !comment.pinned ? 'Pin comment' : 'Unpin comment',
                            pinButton: !comment.pinned ? 'PIN' : 'UNPIN',
                        }}
                    >
                        <button
                            className='pin-button'
                            title= { '$pinnedTitle'  }
                            onClick={ handlePinnedComment }
                        >
                            { '$pinButton' }
                        </button>
                    </Localized>
                : null
                }
            </div>

        </div>
    </li>
}
