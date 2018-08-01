/* global global */

import { configure } from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';

import { URLSearchParams } from 'url';


// Configure enzyme to work with Jest.
configure({ adapter: new Adapter() });

// Make sure URLSearchParams is exposed as in a browser.
// Note: once we update to create-react-app 2.x, we can get rid of this,
// as it uses Jest >22 which uses jsdom >11 which correctly exposes this.
// See https://jestjs.io/blog/2017/12/18/jest-22 and
// https://github.com/facebook/create-react-app/issues/3815
global.URLSearchParams = URLSearchParams;
