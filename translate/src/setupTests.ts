import '@testing-library/jest-dom/vitest';
import { configure } from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';

// @ts-expect-error https://react.dev/reference/react/act#error-the-current-testing-environment-is-not-configured-to-support-act
global.IS_REACT_ACT_ENVIRONMENT = true;

// Configure enzyme to work with vitest.
configure({ adapter: new Adapter() });
