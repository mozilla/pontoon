/* @flow */

import * as React from 'react';
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';

import './Tools.css';

import { History } from 'modules/history';
import { Locales } from 'modules/otherlocales';


type Props = {|
    history: Object,
    otherlocales: Object,
    parameters: Object,
|};


/**
 * Component showing details about an entity.
 *
 * Shows the metadata of the entity and an editor for translations.
 */
export default class Tools extends React.Component<Props> {
    render() {
        const { history, otherlocales, parameters } = this.props;

        const historyCount = history.translations.length;
        const otherlocalesCount = otherlocales.translations.length;

        return <Tabs>
            <TabList>
                <Tab>
                    History
                    { !historyCount ? null :
                    <span className={ 'count' }>{ historyCount }</span>
                    }
                </Tab>
                <Tab>
                    Locales
                    { !otherlocalesCount ? null :
                    <span className={ 'count' }>{ otherlocalesCount }</span>
                    }
                </Tab>
            </TabList>

            <TabPanel>
                <History history={ history } />
            </TabPanel>
            <TabPanel>
                <Locales otherlocales={ otherlocales } parameters={ parameters } />
            </TabPanel>
        </Tabs>;
    }
}
