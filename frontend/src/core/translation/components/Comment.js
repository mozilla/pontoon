/* @flow */

import * as React from 'react';
import ReactTimeAgo from 'react-time-ago';

import { WithPlaceables } from 'core/placeable';
import type { TranslationComment } from 'core/api';


type Props = {|
    comment: TranslationComment,
|};


export default class Comment extends React.Component<Props> {
    renderUserAvatar() {
        const { comment } = this.props;

        if (!comment.author_id) {
            return <img
                src='/static/img/anon.jpg'
                alt=''
                height='44'
                width='44'
            />;
        }

        return <a
            href={ `/contributors/${comment.username}` }
            title='Author'
            target='_blank'
            rel='noopener noreferrer'
            onClick={ (e: SyntheticMouseEvent<>) => e.stopPropagation() }
        >
            <img
                src={ comment.user_gravatar_url_small }
                alt=''
                height='44'
                width='44'
            />
        </a>
    }

    renderUser() {
        const { comment } = this.props;

        if (!comment.author_id) {
            return <span>{ comment.author }</span>;
        }

        return <a
            href={ `/contributors/${comment.username}` }
            title='Author'
            target='_blank'
            rel='noopener noreferrer'
            onClick={ (e: SyntheticMouseEvent<>) => e.stopPropagation() }
        >
            { comment.username }
        </a>
    }

    render() {
        const { comment } = this.props;

        if (!comment) {
            return null;
        }

        var divStyle = { display: 'inline' }

        return (
                <div title='Comment'>
                    <div className='avatar' style={divStyle}>
                        { this.renderUserAvatar() }
                    </div>
                    { this.renderUser() }
                    <WithPlaceables> { comment.content } </WithPlaceables>
                    <div>
                        <ReactTimeAgo
                            dir='ltr'
                            date={ new Date(comment.date_iso) }
                            title={ `${comment.timestamp} UTC` }
                        />
                    </div>
                </div>
        )
    }
}
