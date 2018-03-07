
import React from 'react';

import {DropdownMenu} from 'widgets/menus/dropdown';
import {IconLink} from 'widgets/icons';
import {AvatarLink} from 'widgets/images';
import {SignoutForm} from 'widgets/forms';

import './menu.css';


export class ProfileMenu extends React.PureComponent {

    constructor (props) {
        super(props);
        this.signoutForm;
        this.handleSignout = this.handleSignout.bind(this);
        this.handleFormLoad = this.handleFormLoad.bind(this);
    }

    get isAnon () {
        return !this.props.user || !this.props.user.username;
    }

    get items () {
        let items = [];
        if (!this.isAnon) {
            items = items.concat([this.renderAvatar(), null]);
        }
        Object.entries(this.props.menus || []).forEach(([k, menu], i) => {
            items = items.concat(this.renderMenuItems(menu));
            if (k === 'user' && !this.isAnon) {
                items.push(this.renderSignout());
            }
            if (Object.keys(this.props.menus || []).length > i + 1) {
                items.push(null);
            }
        });
        return items;
    }

    handleFormLoad (form) {
        this.signoutForm = form;
    }

    handleSignout (evt) {
        evt.preventDefault();
        this.signoutForm.submit();
    }

    render () {
        if (!this.props.user) {
            return '';
        }
        return (
            <DropdownMenu
               items={this.items}
               {...this.props} />);
    }

    renderAvatar () {
        const {user} = this.props;
        return (
            <AvatarLink href="/profile/" src={user.avatar}>
              <p className="name">{user.email}</p>
              <p className="email">{user.email}</p>
            </AvatarLink>);
    }

    renderMenuItems (menu) {
        return menu.map(item => (
            <IconLink
               href={item.href}
               icon={item.icon}>
              {item.text}
            </IconLink>));
    }

    renderSignout () {
        const { user} = this.props;
        return (
            <IconLink
               icon="sign-out"
               onClick={this.handleSignout}
               title={user.username}>
                {this.renderSignoutForm()}
                Sign out
            </IconLink>);
    }

    renderSignoutForm () {
        return (
            <SignoutForm
               handleFormLoad={this.handleFormLoad} />);
    }
}
