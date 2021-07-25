import React from 'react';
import { shallow } from 'enzyme';

import GoogleTranslation, {
    GetGoogleTranslateInputFormat,
    GetGoogleTranslateInputText,
    GetGoogleTranslateResponseText,
    GetPlaceables,
} from './GoogleTranslation';

describe ('GetgoogleTranslateInputFormat', () => {
    it('should detect html entities', () => {
        expect(GetGoogleTranslateInputFormat('html &amp; text walk into bar.')).toBe('html');
    });
    it('should detect html tags', function () {
        expect(GetGoogleTranslateInputFormat('html and <h1>text</h1> walk into bar.')).toBe('html');
    });
    it('should detect text without html tags and entities', function () {
        expect(GetGoogleTranslateInputFormat('html and text walk into bar.')).toBe('text');
    });
});
describe('GetGoogleTranslateResponseText', () => {
    const placeablesTestCases = [
        {
            placeableHashes: [' 1placeable01 '],
            placeablesMap: new Map([['%s', '0']]),
            rightToLeft: false,
            expectedResult: ' %s ',
        },
        {
            placeableHashes: [' 0placeable01 '],
            placeablesMap: new Map([['%s', '0']]),
            rightToLeft: false,
            expectedResult: '%s ',
        },
        {
            placeableHashes: [' 0placeable01 '],
            placeablesMap: new Map([['%s', '0']]),
            rightToLeft: true,
            expectedResult: ' %s',
        },
        {
            placeableHashes: [' 1placeable00 '],
            placeablesMap: new Map([['%s', '0']]),
            rightToLeft: false,
            expectedResult: ' %s',
        },
        {
            placeableHashes: [' 1placeable00 '],
            placeablesMap: new Map([['%s', '0']]),
            rightToLeft: true,
            expectedResult: '%s ',
        },


    ];
    placeablesTestCases.forEach((testcase, index) => {
        it(`Multiple placeable hashes[${index}, "${testcase.placeableHashes}", rtl: ${testcase.rightToLeft}]`, () => {
            let inputText = `Test of ${testcase.placeableHashes.join(
                ' ',
            )} as placeables.`;
            expect(
                GetGoogleTranslateResponseText({translation:inputText}, testcase.placeablesMap, testcase.rightToLeft),
            ).toEqual(`Test of${testcase.expectedResult}as placeables.`);
        });
    });
});

describe('GetGoogleTranslateInputText', () => {
    it('No placeables', () => {
        expect(
            GetGoogleTranslateInputText(
                'String without placeables.',
                new Map([]),
            ),
        ).toEqual('String without placeables.');
        expect(
            GetGoogleTranslateInputText(
                'String without %s placeables.',
                new Map([]),
            ),
        ).toEqual('String without %s placeables.');
    });

    const placeablesTestCases = [
        {
            placeables: [' %s '],
            placeablesMap: new Map([['%s', '0']]),
            expectedResult: ' 1placeable01 ',
        },
        {
            placeables: [' %s'],
            placeablesMap: new Map([['%s', '0']]),
            expectedResult: ' 1placeable00 ',
        },
        {
            placeables: ['%s '],
            placeablesMap: new Map([['%s', '0']]),
            expectedResult: ' 0placeable01 ',
        },
        {
            placeables: ['%s'],
            placeablesMap: new Map([['%s', '0']]),
            expectedResult: ' 0placeable00 ',
        },
        {
            placeables: [' %s ', ' %(types)s '],
            placeablesMap: new Map([
                ['%s', '0'],
                ['%(types)s', '1'],
            ]),
            expectedResult: ' 1placeable01 1placeable11 ',
        },
        {
            placeables: [' %s ', '%(types)s '],
            placeablesMap: new Map([
                ['%s', '0'],
                ['%(types)s', '1'],
            ]),
            expectedResult: ' 1placeable01 1placeable11 ',
        },
        {
            placeables: [' %s ', ' %(types)s'],
            placeablesMap: new Map([
                ['%s', '0'],
                ['%(types)s', '1'],
            ]),
            expectedResult: ' 1placeable01 1placeable10 ',
        },
        {
            placeables: [' %s ', '%(types)s'],
            placeablesMap: new Map([
                ['%s', '0'],
                ['%(types)s', '1'],
            ]),
            expectedResult: ' 1placeable01 1placeable10 ',
        },
        {
            placeables: ['%s ', ' %(types)s '],
            placeablesMap: new Map([
                ['%s', '0'],
                ['%(types)s', '1'],
            ]),
            expectedResult: ' 0placeable01 1placeable11 ',
        },
        {
            placeables: ['%s ', '%(types)s '],
            placeablesMap: new Map([
                ['%s', '0'],
                ['%(types)s', '1'],
            ]),
            expectedResult: ' 0placeable01 1placeable11 ',
        },
        {
            placeables: ['%s ', ' %(types)s'],
            placeablesMap: new Map([
                ['%s', '0'],
                ['%(types)s', '1'],
            ]),
            expectedResult: ' 0placeable01 1placeable10 ',
        },
        {
            placeables: ['%s ', '%(types)s'],
            placeablesMap: new Map([
                ['%s', '0'],
                ['%(types)s', '1'],
            ]),
            expectedResult: ' 0placeable01 1placeable10 ',
        },

        {
            placeables: ['%s', ' %(types)s '],
            placeablesMap: new Map([
                ['%s', '0'],
                ['%(types)s', '1'],
            ]),
            expectedResult: ' 0placeable01 1placeable11 ',
        },
        {
            placeables: ['%s', '%(types)s '],
            placeablesMap: new Map([
                ['%s', '0'],
                ['%(types)s', '1'],
            ]),
            expectedResult: ' 0placeable00 0placeable11 ',
        },
        {
            placeables: ['%s', ' %(types)s'],
            placeablesMap: new Map([
                ['%s', '0'],
                ['%(types)s', '1'],
            ]),
            expectedResult: ' 0placeable01 1placeable10 ',
        },
        {
            placeables: ['%s', '%(types)s'],
            placeablesMap: new Map([
                ['%s', '0'],
                ['%(types)s', '1'],
            ]),
            expectedResult: ' 0placeable00 0placeable10 ',
        },
    ];
    placeablesTestCases.forEach((testcase, index) => {
        it(`Multiple placeables[${index}, "${testcase.placeables}"]`, () => {
            let inputText = `Test of${testcase.placeables.join(
                '',
            )}as placeables.`;
            expect(
                GetGoogleTranslateInputText(inputText, testcase.placeablesMap),
            ).toEqual(`Test of${testcase.expectedResult}as placeables.`);
        });
    });
});
describe('GetPlaceables', () => {
    it('Empty string', () => {
        expect(GetPlaceables('')).toEqual(new Map());
    });
    it('Non-empty string without placeables', () => {
        expect(
            GetPlaceables('some random string to test the function.'),
        ).toEqual(new Map());
    });
    it('Detect placeables', () => {
        expect(
            GetPlaceables(
                'Detect %(types)s of placeables and %(types)s of %s something.',
            ),
        ).toEqual(
            new Map([
                ['%(types)s', '0'],
                ['%s', '1'],
            ]),
        );
    });
    it('Blocked placeables', ()  => {
        expect(
            GetPlaceables(
                'Detect %(types)s of placeables and %(types)s of %s something.' +
                'Random &amp; «» <h1>Some other placeables</h1>.',
            ),
        ).toEqual(
            new Map([
                ['%(types)s', '0'],
                ['%s', '1'],
            ]),
        );
    })
});
describe('<GoogleTranslation>', () => {
    it('renders the GoogleTranslation component properly', () => {
        const wrapper = shallow(<GoogleTranslation />);

        expect(wrapper.find('li')).toHaveLength(1);
        expect(wrapper.find('Localized').props().id).toEqual(
            'machinery-GoogleTranslation--visit-google',
        );
        expect(wrapper.find('li a').props().href).toContain(
            'https://translate.google.com/',
        );
        expect(wrapper.find('li a').props().title).toContain(
            'Visit Google Translate',
        );
        expect(wrapper.find('li a span').text()).toEqual('GOOGLE TRANSLATE');
    });
});
