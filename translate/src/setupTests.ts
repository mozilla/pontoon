import { configure } from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';
import '@testing-library/jest-dom';

// @ts-expect-error https://react.dev/reference/react//act#error-the-current-testing-environment-is-not-configured-to-support-act
global.IS_REACT_ACT_ENVIRONMENT = true;

// Configure enzyme to work with Jest.
configure({ adapter: new Adapter() });
