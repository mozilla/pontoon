
import React from 'react';

import {getComponents} from 'utils/components';
import Toolbar from 'components/toolbar';

import DashboardHeader from './header';
import DashboardBody from './body';
import DashboardNavigation from './navigation';


export default class Dashboard extends React.PureComponent {
    components = {
        body: DashboardBody,
        header: DashboardHeader,
        navigation: DashboardNavigation,
        toolbar: Toolbar};

    componentWillMount () {
        if (!this.props.content) {
            this.props.refreshData();
        }
    }

    render () {
        if (!this.props.data || !Object.keys(this.props.data).length) {
            return '';
        }
        const components = getComponents(this);
        const {manager, ...props} = this.props;
        const {content, subtitle, summaryStats, tabs, toolbar, title} = this.props.manager;
        return (
            <div>
              {this.renderToolbar(components.toolbar, toolbar, props)}
              {this.renderHeader(components.header, title, subtitle, summaryStats, props)}
              {this.renderNavigation(components.navigation, tabs, props)}
              {this.renderBody(components.body, content, props)}
            </div>);
    }

    renderBody (Body, content, props) {
        return (
            <Body
               {...props}
               content={content} />);
    }

    renderHeader (Header, title, subtitle, summaryStats, props) {
        return (
            <Header
               {...props}
               title={title}
               subtitle={subtitle}
               stats={summaryStats} />);
    }

    renderNavigation (Navigation, tabs, props) {
        return (
            <Navigation
               {...props}
               tabs={tabs || []} />);
    }

    renderToolbar (Toolbar, toolbar, props) {
        return (
            <header id="toolbar" className="toolbar">
              <Toolbar
                 {...props}
                 toolbar={toolbar} />
            </header>);
    }
}
