/* @flow */

import reducer from './reducer';


// Name of this module.
// Used as the key to store this module's reducer.
const NAME: string = 'navigation';

const constants = {
    NAME,
};


export default {
    constants,
    reducer,
};
