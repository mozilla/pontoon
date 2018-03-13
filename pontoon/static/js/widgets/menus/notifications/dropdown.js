
import React from 'react';

import {DropdownMenuButton} from 'widgets/menus/dropdown';
import NotificationsMenu from './menu';
import NotificationsButton from './button';


export default class NotificationsDropdown extends React.PureComponent {

    get components () {
        return {
            button: NotificationsButton,
            menu: NotificationsMenu};
    }

    render () {
        return (
            <DropdownMenuButton
               {...this.props}
               id="notification"
               className="select"
               components={this.components} />);
    }
}
