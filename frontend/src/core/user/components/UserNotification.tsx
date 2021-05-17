import * as React from 'react';
import Linkify from 'react-linkify';
import parse from 'html-react-parser';
import ReactTimeAgo from 'react-time-ago';

import './UserNotification.css';

type Props = {
    notification: Record<string, any>;
};

type State = {
    markAsRead: boolean;
};

/**
 * Renders a single notification in the notifications menu.
 */
export default class UserNotification extends React.Component<Props, State> {
    constructor(props: Props) {
        super(props);

        this.state = {
            markAsRead: false,
        };
    }

    componentDidUpdate(prevProps: Props) {
        if (prevProps.notification.unread && !this.props.notification.unread) {
            this.setState({
                markAsRead: true,
            });
        }
    }

    render(): React.ReactElement<'li'> {
        const { notification } = this.props;

        let className = 'user-notification';
        let isComment = !notification.description.content
            ? false
            : notification.description.is_comment;
        if (notification.unread) {
            className += ' unread';
        } else if (this.state.markAsRead) {
            className += ' read';
        }

        if (isComment) {
            return (
                <li
                    className={className}
                    data-id={notification.id}
                    data-level={notification.level}
                >
                    <div className='item-content'>
                        <span className='actor'>
                            {notification.actor.anchor}
                        </span>

                        <span className='verb'>
                            <a href={notification.target.url}>
                                {notification.verb}
                            </a>
                        </span>

                        <span className='target'>
                            {notification.target.anchor}
                        </span>

                        <ReactTimeAgo
                            className='timeago'
                            date={new Date(notification.date_iso)}
                            title={`${notification.date} UTC`}
                        />

                        <div className='message trim'>
                            <Linkify
                                properties={{
                                    target: '_blank',
                                    rel: 'noopener noreferrer',
                                }}
                            >
                                {/* We can safely use parse with notification.description.content as it is
                                 *  sanitized when coming from the DB. See:
                                 *    - pontoon.base.forms.AddCommentForm(}
                                 *    - pontoon.base.forms.HtmlField()
                                 */}
                                {parse(notification.description.content)}
                            </Linkify>
                        </div>
                    </div>
                </li>
            );
        }

        return (
            <li
                className={className}
                data-id={notification.id}
                data-level={notification.level}
            >
                <div className='item-content'>
                    <span className='actor'>
                        <a href={notification.actor.url}>
                            {notification.actor.anchor}
                        </a>
                    </span>

                    <span className='verb'>{notification.verb}</span>

                    {!notification.target ? null : (
                        <span className='target'>
                            <a href={notification.target.url}>
                                {notification.target.anchor}
                            </a>
                        </span>
                    )}

                    <ReactTimeAgo
                        className='timeago'
                        date={new Date(notification.date_iso)}
                        title={`${notification.date} UTC`}
                    />

                    {!notification.description.content ? null : (
                        <div
                            className='message'
                            // We can safely use notification.description as it is either generated
                            // by the code or sanitized when coming from the DB. See:
                            //   - pontoon.projects.forms.NotificationsForm()
                            //   - pontoon.base.forms.HtmlField()
                            dangerouslySetInnerHTML={{
                                __html: notification.description.content,
                            }}
                        />
                    )}
                </div>
            </li>
        );
    }
}
