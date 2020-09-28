import React from 'react';
import { shallow } from 'enzyme';

import { FailedChecksBase } from './FailedChecks';

describe('<FailedChecksBase>', () => {
    it('does not render if no errors or warnings present', () => {
        const wrapper = shallow(<FailedChecksBase errors={[]} warnings={[]} />);

        expect(wrapper.find('.failed-checks')).toHaveLength(0);
    });

    it('renders popup with errors and warnings', () => {
        const wrapper = shallow(
            <FailedChecksBase
                errors={['Error1']}
                warnings={['Warning1', 'Warning2']}
            />,
        );

        expect(wrapper.find('.failed-checks')).toHaveLength(1);
        expect(wrapper.find('#editor-FailedChecks--close')).toHaveLength(1);
        expect(wrapper.find('#editor-FailedChecks--title')).toHaveLength(1);
        expect(wrapper.find('.error')).toHaveLength(1);
        expect(wrapper.find('.warning')).toHaveLength(2);
    });

    it('renders save anyway button if translation with warnings submitted', () => {
        const wrapper = shallow(
            <FailedChecksBase
                source={'submitted'}
                errors={[]}
                warnings={['Warning1']}
                user={{
                    settings: {
                        forceSuggestions: false,
                    },
                }}
                isTranslator={true}
            />,
        );

        expect(wrapper.find('.save.anyway')).toHaveLength(1);
    });

    it('renders suggest anyway button if translation with warnings suggested', () => {
        const wrapper = shallow(
            <FailedChecksBase
                source={'submitted'}
                errors={[]}
                warnings={['Warning1']}
                user={{
                    settings: {
                        forceSuggestions: true,
                    },
                }}
            />,
        );

        expect(wrapper.find('.suggest.anyway')).toHaveLength(1);
    });

    it('renders suggest anyway button if user does not have sufficient permissions', () => {
        const wrapper = shallow(
            <FailedChecksBase
                source={'submitted'}
                errors={[]}
                warnings={['Warning1']}
                user={{
                    settings: {
                        forceSuggestions: false,
                    },
                }}
                isTranslator={false}
            />,
        );

        expect(wrapper.find('.suggest.anyway')).toHaveLength(1);
    });

    it('renders approve anyway button if translation with warnings approved', () => {
        const wrapper = shallow(
            <FailedChecksBase
                errors={[]}
                warnings={['Warning1']}
                user={{
                    settings: {
                        forceSuggestions: true,
                    },
                }}
            />,
        );

        expect(wrapper.find('.approve.anyway')).toHaveLength(1);
    });
});
