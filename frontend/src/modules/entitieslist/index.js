/* @flow */

import * as actions from './actions';
import reducer from './reducer';

export { default as EntitiesList } from './components/EntitiesList';


// Name of this module.
// Used as the key to store this module's reducer.
const NAME: string = 'entities';

const constants = {
    NAME,
};


export default {
    actions,
    constants,
    reducer,
};
