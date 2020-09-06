/* @flow */

import * as React from 'react';
import Linkify from 'react-linkify';
import parse from 'html-react-parser';
import ReactTimeAgo from 'react-time-ago';

import './Comment.css';

import { UserAvatar } from 'core/user'

import type { TranslationComment } from 'core/api';
import { Localized } from '@fluent/react';


type Props = {|
    comment: TranslationComment,
|};


export default function Comment(props: Props) {
    const { comment } = props;
    const [ pinned, setPinned ] = React.useState(false);

    if (!comment) {
        return null;
    }

    const handleClick = () => { setPinned(!pinned); }

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
                    { pinned &&
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
                <Localized
                    id="comments-Comment--pin-button"
                    attrs={{ title: true }}
                    vars={{
                        pinnedTitle: !pinned ? 'Pin comment' : 'Unpin comment',
                        pinButton: !pinned ? 'PIN' : 'UNPIN',
                    }}
                >
                    <button 
                        className='pin-button'
                        title= { '$pinnedTitle'  }
                        onClick={ handleClick }
                    >
                        { '$pinButton' }
                    </button>
                </Localized>
            </div>

        </div>
    </li>
}
