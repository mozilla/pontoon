
import React from 'react';

import {NotificationCompose} from './compose';
import {NotificationsList} from './list';


export class NotificationsContent extends React.PureComponent {

    render () {
        if (this.props.content === 'compose') {
            return <NotificationCompose {...this.props} />;
        }
        return <NotificationsList {...this.props} />;
    }
}
