/* @flow */

import * as React from 'react';
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';

import './Tools.css';

import { History } from 'modules/history';


type Props = {|
    historyCount: number,
|};


/**
 * Component showing details about an entity.
 *
 * Shows the metadata of the entity and an editor for translations.
 */
export default class Tools extends React.Component<Props> {
    render() {
        const { historyCount } = this.props;

        return <Tabs>
            <TabList>
                <Tab>
                    History
                    <span className={ 'count' }>{ historyCount }</span>
                </Tab>
                <Tab>Locales</Tab>
            </TabList>

            <TabPanel>
                <History />
            </TabPanel>
            <TabPanel>
                <p>Locales</p>
            </TabPanel>
        </Tabs>;
    }
}
