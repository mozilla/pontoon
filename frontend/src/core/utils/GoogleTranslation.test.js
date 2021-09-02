import React from 'react';

import {
    GetPlaceableLabel,
    GetGoogleTranslateInputFormat,
    GetGoogleTranslateInputText,
    GetGoogleTranslateResponseText,
    GetPlaceables,
    GoogleValidatePlaceables,
} from './GoogleTranslation';

const f = (a, b) => [].concat(...a.map((d) => b.map((e) => [].concat(d, e))));
const cartesianProduct = (a, b, ...c) =>
    b ? cartesianProduct(f(a, b), ...c) : a;

describe('GetPlaceableLabel', () => {
    it.each(cartesianProduct(['0', '1'], [true, false], [true, false]))(
        'should encode a placeable with information about the wrapping spaces (%s, %s, %s, %s)',
        (index, leftSpace, rightSpace) => {
            expect(GetPlaceableLabel(index, leftSpace, rightSpace)).toEqual(
                `${leftSpace ? '1' : '0'}placeable${index}${
                    rightSpace ? '1' : '0'
                }`,
            );
        },
    );
});

describe('GoogleValidatePlaceables', () => {
    it("should success when there's no placeables", () => {
        expect(GoogleValidatePlaceables('test string', new Map())).toEqual(
            true,
        );
    });

    it('should success when all of the placeables are in the string', () => {
        expect(
            GoogleValidatePlaceables(
                'test %s %d',
                new Map([
                    ['%s', '0'],
                    ['%d', '1'],
                ]),
            ),
        ).toEqual(true);
    });

    it('should fail when any of the placeables is missing', () => {
        expect(
            GoogleValidatePlaceables(
                'test %s %d',
                new Map([
                    ['%s', '0'],
                    ['%d', '1'],
                    ['%c', '2'],
                ]),
            ),
        ).toEqual(false);
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
                'html and <h1>text</h1> walk into a bar...',
            ),
        ).toEqual('html');
    });

    it('should recognize text without html tags and entities', function () {
        expect(
            GetGoogleTranslateInputFormat('html and text walk into bar.'),
        ).toEqual('text');
    });
});

describe('GetGoogleTranslateResponseText', () => {
    it.each(
        cartesianProduct(
            // placeable labels
            ['1placeable11', '1placeable10'],
            // left punctuation char
            ['', ',', '"', '√'],
            // right punctuation char
            ['', ',', '"', '™'],
            // RTL
            [true, false],
        ),
    )(
        `should remove wrapping spaces when punctuation characters wrap the placeable (%s)`,
        (placeableLabel, leftPunctuationChar, rightPunctuationChar, rtl) => {
            expect(
                GetGoogleTranslateResponseText(
                    `The security policy blocks ${leftPunctuationChar} ${placeableLabel} ${rightPunctuationChar} because of something.`,
                    new Map([['{ $hostname }', '1']]),
                    rtl,
                ),
            ).toEqual(
                `The security policy blocks ${leftPunctuationChar}{ $hostname }${rightPunctuationChar} because of something.`,
            );
        },
    );
    const placeablesTestCases = [
        [' 1placeable01 ', ' %s ', false],
        [' 0placeable01 ', '%s ', false],
        [' 0placeable01 ', ' %s', true],
        [' 1placeable00 ', ' %s', false],
        [' 1placeable00 ', ' %s', false],
        [' 1placeable00 ', '%s ', true],
    ];

    it.each(placeablesTestCases)(
        `should replace the placeable labels in the middle of the string (%s, %s, %s)`,
        (placeableLabels, expectedResult, rightToLeft) => {
            const inputText = `Test of ${placeableLabels} as placeables.`
                .trim()
                .replace(/ {2}/gi, ' ');

            expect(
                GetGoogleTranslateResponseText(
                    inputText,
                    new Map([['%s', '0']]),
                    rightToLeft,
                ),
            ).toEqual(`Test of${expectedResult}as placeables.`);
        },
    );

    it.each(placeablesTestCases)(
        `should replace the placeable labels at the begin of the string (%s, %s, %s)`,
        (placeableLabels, expectedResult, rightToLeft) => {
            const inputText = `${placeableLabels} as placeables.`
                .trim()
                .replace(/ {2}/gi, ' ');

            expect(
                GetGoogleTranslateResponseText(
                    inputText,
                    new Map([['%s', '0']]),
                    rightToLeft,
                ),
            ).toEqual(`${expectedResult}as placeables.`.trim());
        },
    );

    it.each(placeablesTestCases)(
        `should replace the placeable labels at the end of the string (%s)`,
        (placeableLabels, expectedResult, rightToLeft) => {
            const inputText = `Test of ${placeableLabels}`
                .trim()
                .replace(/ {2}/gi, ' ');

            expect(
                GetGoogleTranslateResponseText(
                    inputText,
                    new Map([['%s', '0']]),
                    rightToLeft,
                ),
            ).toEqual(`Test of${expectedResult}`.trim());
        },
    );
});

describe('GetGoogleTranslateInputText', () => {
    it("should return the string's contents when the map of placeables is empty", () => {
        expect(
            GetGoogleTranslateInputText(
                'String without %s placeables.',
                new Map([]),
            ),
        ).toEqual('String without %s placeables.');
    });

    it.each([
        [' %s ', ' 1placeable01 '],
        [' %s', ' 1placeable00 '],
        ['%s ', ' 0placeable01 '],
        ['%s', ' 0placeable00 '],
        [' %s  %(types)s ', ' 1placeable01 1placeable11 '],
        [' %s %(types)s ', ' 1placeable01 1placeable11 '],
        [' %s  %(types)s', ' 1placeable01 1placeable10 '],
        [' %s %(types)s', ' 1placeable01 1placeable10 '],
        ['%s  %(types)s ', ' 0placeable01 1placeable11 '],
        ['%s %(types)s ', ' 0placeable01 1placeable11 '],
        ['%s  %(types)s', ' 0placeable01 1placeable10 '],
        ['%s %(types)s', ' 0placeable01 1placeable10 '],
        ['%s %(types)s ', ' 0placeable01 1placeable11 '],
        ['%s%(types)s ', ' 0placeable00 0placeable11 '],
        ['%s %(types)s', ' 0placeable01 1placeable10 '],
        ['%s%(types)s', ' 0placeable00 0placeable10 '],
    ])(
        `should replace the placeables with their labels (%s)`,
        (placeables, expectedResult) => {
            const inputText = `Test of${placeables}as placeables.`;

            expect(
                GetGoogleTranslateInputText(
                    inputText,

                    new Map([
                        ['%s', '0'],
                        ['%(types)s', '1'],
                    ]),
                ),
            ).toEqual(`Test of${expectedResult}as placeables.`);
        },
    );
});

describe('GetPlaceables', () => {
    it('should return empty map when  the string is empty', () => {
        expect(GetPlaceables('')).toEqual(new Map());
    });

    it("should return empty map when the string doesn't contain placeables", () => {
        expect(
            GetPlaceables('some random string to test the function.'),
        ).toEqual(new Map());
    });

    it('should return the map of placeables', () => {
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
    it.each(['&amp;', '«', '»', '<h1>'])(
        "shouldn't return the excluded placeables (%s)",
        (excludedPlaceable) => {
            expect(
                GetPlaceables(
                    `Detect %(types)s of placeables and %(types)s of %s something.Random ${excludedPlaceable} other placeables.`,
                ),
            ).toEqual(
                new Map([
                    ['%(types)s', '0'],
                    ['%s', '1'],
                ]),
            );
        },
    );
});
