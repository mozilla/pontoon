
import React from 'react';

import {NotificationsDropdown, ProfileDropdown} from 'widgets/menus';
import {Menu} from 'widgets/menus/generic';


export default class ToolbarMenu extends React.PureComponent {

    get items () {
        const items = [];
        if (this.props.toolbar && this.props.toolbar.user && this.props.toolbar.user.username) {
            items.push(<NotificationsDropdown toolbar={this.props.toolbar} />)
        }
        items.push(<ProfileDropdown {...this.props} />);
        return items;
    }

    render () {
        return <Menu items={this.items} className='menus' />
    }
}
