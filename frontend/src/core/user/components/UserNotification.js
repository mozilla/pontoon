/* @flow */

import * as React from 'react';
import TimeAgo from 'react-timeago';

import './UserNotification.css';


type Props = {
    notification: Object,
};


/**
 * Renders a single notification in the notifications menu.
 */
export default class UserNotification extends React.Component<Props> {
    render() {
        const { notification } = this.props;

        return <li
            className = "user-notification"
            data-id={ notification.id }
            data-level={ notification.level }
            data-unread={ notification.unread }
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
                    date={ notification.date_iso }
                    title={ `${notification.date} UTC` }
                />

                { !notification.description ? null :
                    <div
                        className="message"
                        dangerouslySetInnerHTML={{ __html: notification.description }}
                    />
                }
            </div>
        </li>;
    }
}
