
import React from 'react';

import {TabList} from 'widgets/lists/tabs';
import {Section} from 'widgets/section';


export default class DashboardNavigation extends React.PureComponent {

    get components () {
        const components = {tabs: TabList};
        return Object.assign({}, components, (this.props.components || {}));
    }

    render () {
        const {tabs: Tabs} = this.components;
        return (
            <Section id="middle">
              <Tabs {...this.props} />
            </Section>);
    }
}
