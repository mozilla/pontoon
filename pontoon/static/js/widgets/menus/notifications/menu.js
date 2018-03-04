
import React from 'react';

import {DropdownMenu} from 'widgets/menus/dropdown';
import {Icon} from 'widgets/icons';

import {Notification} from 'widgets/notifications/notification';


export default class NotificationsMenu extends React.PureComponent {

    get items () {
        const items = [];
        const {notifications} = this.props.toolbar;
        if (notifications.length === 0) {
            items.push(this.renderNoNotifications());
        } else {
            notifications.forEach(notification => {
                items.push(this.renderNotification(notification));
            });
        }
        return items.concat([
            null,
            this.renderNotificationsLink()]);
    }

    render () {
        return <DropdownMenu {...this.props} items={this.items} />;
    }

    renderNotificationsLink () {
        return (
            <div className="see-all">
              <a href="/notifications/">See all Notifications</a>
            </div>);
    }

    renderNotification (notification) {
        return <Notification {...notification} />;
    }

    renderNoNotifications () {
        return (
            <div className="no-notifications">
              <Icon name="bell" />
              <p className="title">No new notifications.</p>
              <p className="description">Here you’ll see updates for localizations you contribute to.</p>
            </div>);
    }
}
