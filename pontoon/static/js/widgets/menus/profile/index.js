
import React from 'react';

import {DropdownMenuButton} from 'widgets/menus/dropdown';
import {ProfileMenu} from './menu';
import {Avatar} from 'widgets/images';
import {Icon} from 'widgets/icons';


export class ProfileDropdown extends React.PureComponent {

    get buttonProps () {
        if (!this.props.toolbar.user.avatar) {
            return {
                name: 'navicon',
                className: 'rounded'};
        }
        return {
            src: this.props.toolbar.user.avatar,
            className: 'rounded'};
    }

    get components () {
        let button = Avatar;
        if (!this.props.toolbar.user.avatar) {
            button = Icon;
        }
        return {
            button: button,
            menu: ProfileMenu};
    }

    get menuProps () {
        return {
            user: this.props.toolbar.user,
            menus: this.props.toolbar.menus};
    }

    render () {
        if (!this.props.toolbar || !this.props.toolbar.user) {
            return '';
        }
        return (
            <DropdownMenuButton
               buttonProps={this.buttonProps}
               menuProps={this.menuProps}
               id="profile"
               className="select"
               components={this.components} />);
    }
}
