
import React from 'react';

import {getComponent} from 'utils/components';
import {Section} from 'widgets/section';


export default class DashboardBody extends React.PureComponent {
    id = 'main';

    render () {
        const {components, ...props} = this.props;
        const Content = getComponent(this, 'content');
        if (!Content) {
            return '';
        }
        return (
            <Section id={this.id}>
              <Content {...props} />
            </Section>);
    }
}
