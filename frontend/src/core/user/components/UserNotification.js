/* @flow */

import * as React from 'react';
import TimeAgo from 'react-timeago';

import './UserNotification.css';


type Props = {
    notification: Object,
};

type State = {|
    markAsRead: boolean,
|};


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

    render() {
        const { notification } = this.props;

        let className = 'user-notification';
        if (notification.unread) {
            className += ' unread';
        }
        else if (this.state.markAsRead) {
            className += ' read';
        }

        return <li
            className={ className }
            data-id={ notification.id }
            data-level={ notification.level }
        >
            <div className="item-content">
                <span className="actor">
                    <a href={ notification.actor.url }>
                        { notification.actor.anchor }
                    </a>
                </span>

                <span className="verb">{ notification.verb }</span>

                { !notification.target ? null :
                    <span className="target">
                        <a href={ notification.target.url }>
                            { notification.target.anchor }
                        </a>
                    </span>
                }

                <TimeAgo
                    className="timeago"
                    date={ new Date(notification.date_iso) }
                    title={ `${notification.date} UTC` }
                />

                { !notification.description ? null :
                    <div
                        className="message"
                        // We can safely use notification.description as it is either generated
                        // by the code or sanitized when coming from the DB. See:
                        //   - pontoon.projects.forms.NotificationsForm()
                        //   - pontoon.base.forms.HtmlField()
                        dangerouslySetInnerHTML={{ __html: notification.description }}
                    />
                }
            </div>
        </li>;
    }
}
