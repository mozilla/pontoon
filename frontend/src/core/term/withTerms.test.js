import React from 'react';
import { shallow } from 'enzyme';

import { markTerms } from './withTerms';


describe('markTerms', () => {
    it('marks terms properly', () => {
        const string = 'foo bar baz';
        const terms = {
            terms: [
                {
                    text: 'bar'
                },
                {
                    text: 'baz'
                },
            ]
        };

        const marked = markTerms(string, terms);
        const wrapper = shallow(<p>{ marked }</p>);

        expect(wrapper.find('mark')).toHaveLength(2);
        expect(wrapper.find('mark').at(0).text()).toEqual('bar');
        expect(wrapper.find('mark').at(1).text()).toEqual('baz');
    });

    it('marks entire words on partial match', () => {
        const string = 'Download Add-Ons from the web.';
        const terms = {
            terms: [
                {
                    text: 'add-on'
                },
            ]
        };

        const marked = markTerms(string, terms);
        const wrapper = shallow(<p>{ marked }</p>);

        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual('Add-Ons');
    });

    it('only marks terms at the beginning of the word', () => {
        const string = 'Consider using one of the alternatives.';
        const terms = {
            terms: [
                {
                    text: 'native'
                },
            ]
        };

        const marked = markTerms(string, terms);
        const wrapper = shallow(<p>{ marked }</p>);

        expect(wrapper.find('mark')).toHaveLength(0);
    });

    it('marks longer terms first', () => {
        const string = 'This is a translation tool.';
        const terms = {
            terms: [
                {
                    text: 'translation'
                },
                {
                    text: 'translation tool'
                },
            ]
        };

        const marked = markTerms(string, terms);
        const wrapper = shallow(<p>{ marked }</p>);

        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual('translation tool');
    });
});
