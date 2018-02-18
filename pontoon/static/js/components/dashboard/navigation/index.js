
import React from 'react';

import {Link} from 'react-router-dom';

import {getComponent, getComponents} from 'utils/components';
import {ListItem} from 'widgets/lists/generic';
import {TabList} from 'widgets/lists/tabs';
import {Section} from 'widgets/section';


class TabLink extends React.PureComponent {

    render () {
        const TabCount = getComponent(this, 'count');
        const className = this.props.activeTab === this.props.href ? 'active tab link' : 'tab link';
        return (
            <ListItem
               className={className}>
              <Link to={this.props.href}>
                {this.props.children}
                <TabCount count={this.props.count} />
              </Link>
            </ListItem>);
    }
}


export default class DashboardNavigation extends React.PureComponent {
    components = {tabs: TabList, tab: TabLink};

    render () {
        const {href, tabs} = this.props;
        const {tabs: Tabs, tab: item} = getComponents(this);
        return (
            <Section id="middle">
              <Tabs
                 components={{item}}
                 activeTab={href}
                 tabs={tabs} />
            </Section>);
    }
}
