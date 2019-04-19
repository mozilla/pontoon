import React from 'react';
import { shallow } from 'enzyme';

import FailedChecks from './FailedChecks';


describe('<FailedChecks>', () => {
    it('do not render if no errors or warnings present', () => {
        const wrapper = shallow(<FailedChecks
            errors={ [] }
            warnings={ [] }
        />);

        expect(wrapper.find('.failed-checks')).toHaveLength(0);
    });

    it('render popup with errors and warnings', () => {
        const wrapper = shallow(<FailedChecks
            errors={ ['Error1'] }
            warnings={ ['Warning1', 'Warning2'] }
        />);

        expect(wrapper.find('.failed-checks')).toHaveLength(1);
        expect(wrapper.find('#editor-FailedChecks--close')).toHaveLength(1);
        expect(wrapper.find('#editor-FailedChecks--title')).toHaveLength(1);
        expect(wrapper.find('.error')).toHaveLength(1);
        expect(wrapper.find('.warning')).toHaveLength(2);
    });

    it('render save anyway button if translation with warnings submitted', () => {
        const wrapper = shallow(<FailedChecks
            source={ 'submitted' }
            errors={ [] }
            warnings={ ['Warning1'] }
            user={ {
                settings: {
                    forceSuggestions: false,
                },
            } }
        />);

        expect(wrapper.find('.save.anyway')).toHaveLength(1);
    });

    it('render suggest anyway button if translation with warnings suggested', () => {
        const wrapper = shallow(<FailedChecks
            source={ 'submitted' }
            errors={ [] }
            warnings={ ['Warning1'] }
            user={ {
                settings: {
                    forceSuggestions: true,
                },
            } }
        />);

        expect(wrapper.find('.suggest.anyway')).toHaveLength(1);
    });

    it('render approve anyway button if translation with warnings approved', () => {
        const wrapper = shallow(<FailedChecks
            errors={ [] }
            warnings={ ['Warning1'] }
            user={ {
                settings: {
                    forceSuggestions: true,
                },
            } }
        />);

        expect(wrapper.find('.approve.anyway')).toHaveLength(1);
    });
});
