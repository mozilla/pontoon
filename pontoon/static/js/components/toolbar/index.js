
import React from 'react';

import {getComponents} from 'utils/components';
import {Logo} from 'widgets/images';
import {LinkList} from 'widgets/lists/links';

import ToolbarMenu from './menu';
import './toolbar.css';


export default class Toolbar extends React.PureComponent {
    components = {
        icon: Logo,
        links: LinkList,
        menu: ToolbarMenu};

    render () {
        if (!this.props.toolbar) {
            return '';
        }
        const {
            icon: ToolbarIcon,
            links: ToolbarLinks,
            menu: ToolbarMenu} = getComponents(this);
        return (
            <nav>
              <ToolbarIcon {...this.props.toolbar.logo} />
              <ToolbarLinks {...this.props.toolbar} />
              <ToolbarMenu {...this.props} />
            </nav>);
    }
}
