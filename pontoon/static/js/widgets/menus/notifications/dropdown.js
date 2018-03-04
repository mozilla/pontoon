
import React from 'react';

import {getComponents} from 'utils/components';
import {DropdownMenuButton} from 'widgets/menus/dropdown';

import NotificationsMenu from './menu';
import NotificationsButton from './button';


export default class NotificationsDropdown extends React.PureComponent {
    components = {
        button: NotificationsButton,
        menu: NotificationsMenu};

    render () {
        return (
            <DropdownMenuButton
               components={getComponents(this)}
               {...this.props}
               id="notification"
               className="select" />);
    }
}
