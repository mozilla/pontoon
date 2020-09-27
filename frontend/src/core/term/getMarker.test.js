import React from 'react';
import { shallow } from 'enzyme';

import getMarker from './getMarker';

describe('markTerms', () => {
    it('marks terms properly', () => {
        const string = 'foo bar baz';
        const terms = {
            terms: [
                {
                    text: 'bar',
                },
                {
                    text: 'baz',
                },
            ],
        };

        const TermsAndPlaceablesMarker = getMarker(terms);
        const wrapper = shallow(
            <TermsAndPlaceablesMarker>{string}</TermsAndPlaceablesMarker>,
        );

        expect(wrapper.find('mark')).toHaveLength(2);
        expect(wrapper.find('mark').at(0).text()).toEqual('bar');
        expect(wrapper.find('mark').at(1).text()).toEqual('baz');
    });

    it('marks entire words on partial match', () => {
        const string = 'Download Add-Ons from the web.';
        const terms = {
            terms: [
                {
                    text: 'add-on',
                },
            ],
        };

        const TermsAndPlaceablesMarker = getMarker(terms);
        const wrapper = shallow(
            <TermsAndPlaceablesMarker>{string}</TermsAndPlaceablesMarker>,
        );

        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual('Add-Ons');
    });

    it('only marks terms at the beginning of the word', () => {
        const string = 'Consider using one of the alternatives.';
        const terms = {
            terms: [
                {
                    text: 'native',
                },
            ],
        };

        const TermsAndPlaceablesMarker = getMarker(terms);
        const wrapper = shallow(
            <TermsAndPlaceablesMarker>{string}</TermsAndPlaceablesMarker>,
        );

        expect(wrapper.find('mark')).toHaveLength(0);
    });

    it('marks longer terms first', () => {
        const string = 'This is a translation tool.';
        const terms = {
            terms: [
                {
                    text: 'translation',
                },
                {
                    text: 'translation tool',
                },
            ],
        };

        const TermsAndPlaceablesMarker = getMarker(terms);
        const wrapper = shallow(
            <TermsAndPlaceablesMarker>{string}</TermsAndPlaceablesMarker>,
        );

        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual('translation tool');
    });

    it('does not mark terms within placeables', () => {
        const string =
            'This browser { $version } does not support { $bits }-bit systems.';
        const terms = {
            terms: [
                {
                    text: 'browser',
                },
                {
                    text: 'version',
                },
            ],
        };

        const TermsAndPlaceablesMarker = getMarker(terms);
        const wrapper = shallow(
            <TermsAndPlaceablesMarker>{string}</TermsAndPlaceablesMarker>,
        );

        expect(wrapper.find('mark')).toHaveLength(3);
        expect(wrapper.find('mark').at(0).text()).toEqual('browser');
        expect(wrapper.find('mark').at(0).hasClass('term'));
        expect(wrapper.find('mark').at(1).text()).toEqual('{ $version }');
        expect(wrapper.find('mark').at(1).hasClass('placeable'));
        expect(wrapper.find('mark').at(2).text()).toEqual('{ $bits }');
        expect(wrapper.find('mark').at(2).hasClass('placeable'));
    });
});
