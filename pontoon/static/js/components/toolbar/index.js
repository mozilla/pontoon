
import React from 'react';

import {Logo} from 'widgets/images';
import {LinkList} from 'widgets/lists/links';

import ToolbarMenu from './menu';

import './toolbar.css';


export default class Toolbar extends React.PureComponent {

    get components () {
        const components = {
            icon: Logo,
            links: LinkList,
            menu: ToolbarMenu};
        return Object.assign({}, components, (this.props.components || {}));
    }

    render () {
        if (!this.props.toolbar) {
            return '';
        }
        const {
            icon: ToolbarIcon,
            links: ToolbarLinks,
            menu: ToolbarMenu} = this.components;
        return (
            <nav>
              <ToolbarIcon {...this.props.toolbar.logo} />
              <ToolbarLinks {...this.props.toolbar} />
              <ToolbarMenu {...this.props} />
            </nav>);
    }
}
