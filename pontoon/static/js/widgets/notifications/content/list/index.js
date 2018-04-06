
import React from 'react';

import {List} from 'widgets/lists/generic';
import {Icon} from 'widgets/icons';
import {Notification} from 'widgets/notifications/notification';


export class NotificationsList extends React.PureComponent {

    get items () {
        if (!this.props.notifications) {
            return {value: this.renderNoNotifications()};
        }
        return Object.values(this.props.notifications).map(notification => ({value: <Notification {...notification}/>}));
    }

    render () {
        return <List className="notfications-widget" items={this.items} />;
    }

    renderNoNotifications () {
        return [<Icon name="bell" />,
                <p className="title">NO TITLE</p>,
                <p className="description">NO DESCRIPTION</p>];
    }
}
