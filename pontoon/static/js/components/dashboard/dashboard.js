
import 'base/fonts';

import './style.css';
import './dashboard.css';

import React from 'react';
import DashboardHeader from './header';
import DashboardBody from './body';
import DashboardNavigation from './navigation';
import Toolbar from 'components/toolbar';

import './unhide.css';


export default class Dashboard extends React.PureComponent {

    get components () {
        const components = {
            body: DashboardBody,
            header: DashboardHeader,
            navigation: DashboardNavigation,
            toolbar: Toolbar};
        return Object.assign({}, components, this.props.manager.components);
    }

    componentDidMount () {
        this.props.refreshData();
    }

    render () {
        if (!this.props.data || !Object.keys(this.props.data).length) {
            return '';
        }
        return (
            <div>
              {this.renderToolbar()}
              {this.renderHeader()}
              {this.renderNavigation()}
              {this.renderBody()}
            </div>);
    }

    renderBody () {
        const {body: Body} = this.components;
        return (
            <Body
               {...this.props}
               content={this.props.manager.content}
               components={this.components}
               />);
    }

    renderHeader () {
        const {header: Header} = this.components;
        return (
            <Header
               {...this.props}
               title={this.props.manager.title}
               subtitle={this.props.manager.subtitle}
               stats={this.props.manager.summaryStats}
               components={this.components}
               />);
    }

    renderNavigation () {
        const {navigation: Navigation} = this.components;
        return (
            <Navigation
               {...this.props}
               tabs={this.props.manager.tabs || []}
               components={this.components}
               />);
    }

    renderToolbar () {
        const {toolbar: Toolbar} = this.components;
        return (
            <header id="toolbar" className="toolbar">
                <Toolbar
                   {...this.props}
                   toolbar={this.props.manager.toolbar}
                   components={this.components}
                   />
            </header>);
    }
}
