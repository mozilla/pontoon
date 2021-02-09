import { configure } from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';

// Configure enzyme to work with Jest.
configure({ adapter: new Adapter() });
