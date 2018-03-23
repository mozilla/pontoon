
import React from 'react';

import {Menu} from 'widgets/menus/generic';


export class NotificationsMenu extends React.Component {
    state = {active: 'compose'}

    handleClick = (evt) => {
        evt.preventDefault();
        this.setState({active: evt.currentTarget.name});
    }

    get items () {
        const {active} = this.state;
        return [
            this.renderComposeClick(active),
            null,
            this.renderSendClick(active)];
    }

    componentDidUpdate (prevProps, prevState) {
        if (prevState !== this.state) {
            this.props.handleMenuChange(this.state.active);
        }
    }

    render () {
        return <Menu className="notifications-menu" items={this.items} />;
    }

    renderComposeClick (active) {
        return (
            <a onClick={this.handleClick}
               className={active === 'compose' ? 'active' : ''}
               name="compose">Compose</a>);
    }

    renderSendClick (active) {
        let count = 0;
        if (this.props.notifications) {
            count = Object.keys(this.props.notifications).length;
        }
        return (
            <a onClick={this.handleClick}
               className={active === 'sent' ? 'active' : ''}
               name="sent">
              <span className="name">Sent</span>
              <span className="count">{count}</span>
            </a>);
    }
}
