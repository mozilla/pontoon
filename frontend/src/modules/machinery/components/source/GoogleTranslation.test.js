import React from 'react';
import { shallow } from 'enzyme';

import GoogleTranslation, {
    GetGoogleTranslateInputFormat,
    GetGoogleTranslateInputText,
    GetGoogleTranslateResponseText,
    GetPlaceableHash,
    GetPlaceables,
} from './GoogleTranslation';

describe('GetPlaceableHash', () => {
    it('generates placeable hash based on an index and adds information about the surrounding spaces', () => {
        expect(GetPlaceableHash('0', false, false)).toEqual('0placeable00');
        expect(GetPlaceableHash('0', true, false)).toEqual('1placeable00');
        expect(GetPlaceableHash('0', false, true)).toEqual('0placeable01');
        expect(GetPlaceableHash('0', true, true)).toEqual('1placeable01');
    });
});

describe('GetGoogleTranslateInputFormat', () => {
    it('should detect html entities', () => {
        expect(
            GetGoogleTranslateInputFormat('html &amp; text walk into bar.'),
        ).toEqual('html');
    });
    it('should detect html tags', function () {
        expect(
            GetGoogleTranslateInputFormat(
                'html and <h1>text</h1> walk into bar.',
            ),
        ).toEqual('html');
    });
    it('should detect text without html tags and entities', function () {
        expect(
            GetGoogleTranslateInputFormat('html and text walk into bar.'),
        ).toEqual('text');
    });
});

describe('GetGoogleTranslateResponseText', () => {
    it('checks example responses', () => {
        const inputText = "The server is redirecting the \"URI\" for the calendar “ 0placeable10 ” & 1 > 2 > 5.¶ 0placeable00";
        expect(GetGoogleTranslateResponseText(
            {translation: inputText},
            new Map([
                ["¶", "0"],
                ["{ $calendarName }", "1"],
            ]),
            false
        )).toEqual('The server is redirecting the "URI" for the calendar “{ $calendarName }” & 1 > 2 > 5.¶¶')

        expect(GetGoogleTranslateResponseText(
            {translation: inputText},
            new Map([
                ["¶", "0"],
                ["{ $calendarName }", "1"],
            ]),
            true
        )).toEqual('The server is redirecting the "URI" for the calendar “{ $calendarName }” & 1 > 2 > 5.¶¶')
    });

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
        it(`returns translation and replaces the placeable hashes [${index}, "${testcase.placeableHashes}", rtl: ${testcase.rightToLeft}]`, () => {
            const inputText = `Test of ${testcase.placeableHashes.join(
                ' ',
            )} as placeables.`.trim().replace(/ {2}/gi, ' ');
            expect(
                GetGoogleTranslateResponseText(
                    { translation: inputText },
                    testcase.placeablesMap,
                    testcase.rightToLeft,
                ),
            ).toEqual(`Test of${testcase.expectedResult}as placeables.`);
        });

        it(`returns translation and replaces the placeable hashes (starting from left) [${index}, "${testcase.placeableHashes}", rtl: ${testcase.rightToLeft}]`, () => {
            const inputText = `${testcase.placeableHashes.join(
                ' ',
            )} as placeables.`;
            expect(
                GetGoogleTranslateResponseText(
                    { translation: inputText },
                    testcase.placeablesMap,
                    testcase.rightToLeft,
                ),
            ).toEqual(`${testcase.expectedResult}as placeables.`.trim());
        });

        it(`returns translation and replaces the placeable hashes (starting from right) [${index}, "${testcase.placeableHashes}", rtl: ${testcase.rightToLeft}]`, () => {
            const inputText = `Test of ${testcase.placeableHashes.join(
                ' ',
            )}`.trim();
            expect(
                GetGoogleTranslateResponseText(
                    { translation: inputText },
                    testcase.placeablesMap,
                    testcase.rightToLeft,
                ),
            ).toEqual(`Test of${testcase.expectedResult}`.trim());
        });
    });
});

describe('GetGoogleTranslateInputText', () => {
    it('return text when the placeables map is empty', () => {
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
        it(`replace the placeables with their hashes [${index}, "${testcase.placeables}"]`, () => {
            const inputText = `Test of${testcase.placeables.join(
                '',
            )}as placeables.`;
            expect(
                GetGoogleTranslateInputText(inputText, testcase.placeablesMap),
            ).toEqual(`Test of${testcase.expectedResult}as placeables.`);
        });

        it(`replace placeables with their hashes (starting from left) [${index}, "${testcase.placeables}"]`, () => {
            const inputText = `${testcase.placeables.join('')}as placeables.`;
            expect(
                GetGoogleTranslateInputText(inputText, testcase.placeablesMap),
            ).toEqual(`${testcase.expectedResult}as placeables.`.trim());
        });

        it(`replace placeables with their hashes (starting from right) [${index}, "${testcase.placeables}"]`, () => {
            const inputText = `Test of${testcase.placeables.join('')}`;
            expect(
                GetGoogleTranslateInputText(inputText, testcase.placeablesMap),
            ).toEqual(`Test of${testcase.expectedResult}`.trim());
        });
    });
});

describe('GetPlaceables', () => {
    it('returns empty map when  the string is empty', () => {
        expect(GetPlaceables('')).toEqual(new Map());
    });

    it("returns empty map when the string doesn't contain placeables", () => {
        expect(
            GetPlaceables('some random string to test the function.'),
        ).toEqual(new Map());
    });

    it('return the map of placeables', () => {
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
    it("don't return the blocked placeables in the map", () => {
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
    });
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
