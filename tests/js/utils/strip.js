import { Strip, strip } from 'utils/strip';

test('Strip instance', () => {
    expect(strip instanceof Strip).toBe(true);
});

test('Strip lstrip', () => {
    const _strip = new Strip();
    expect(_strip.lstrip('aaaxyz', 'a')).toBe('xyz');
    expect(_strip.lstrip('aaaxyz', 'b')).toBe('aaaxyz');
    expect(_strip.lstrip('abaxyz', 'b')).toBe('abaxyz');
    expect(_strip.lstrip('bbaxyz', 'b')).toBe('axyz');
    expect(_strip.lstrip('bbaxyzbbb', 'b')).toBe('axyzbbb');
    expect(_strip.lstrip('   bbaxyz')).toBe('bbaxyz');
    expect(_strip.lstrip('   bb   axyz')).toBe('bb   axyz');
    expect(_strip.lstrip('   bb   axyz   ')).toBe('bb   axyz   ');
});

test('Strip rstrip', () => {
    const _strip = new Strip();
    expect(_strip.rstrip('xyzaaa', 'a')).toBe('xyz');
    expect(_strip.rstrip('xyzaaa', 'b')).toBe('xyzaaa');
    expect(_strip.rstrip('xyzaba', 'b')).toBe('xyzaba');
    expect(_strip.rstrip('xyzbba', 'b')).toBe('xyzbba');
    expect(_strip.rstrip('bbaxyzbbb', 'b')).toBe('bbaxyz');
    expect(_strip.rstrip('bbaxyz   ')).toBe('bbaxyz');
    expect(_strip.rstrip('bb   axyz   ')).toBe('bb   axyz');
    expect(_strip.rstrip('   bb   axyz   ')).toBe('   bb   axyz');
});

test('Strip strip', () => {
    const _strip = new Strip();
    expect(_strip.strip('xyzaaa', 'a')).toBe('xyz');
    expect(_strip.strip('xyzaaa', 'b')).toBe('xyzaaa');
    expect(_strip.strip('xyzaba', 'b')).toBe('xyzaba');
    expect(_strip.strip('xyzbba', 'b')).toBe('xyzbba');
    expect(_strip.strip('bbaxyzbbb', 'b')).toBe('axyz');
    expect(_strip.strip('bbabbaxyzbbabbb', 'b')).toBe('abbaxyzbba');
    expect(_strip.strip('bbaxyz   ')).toBe('bbaxyz');
    expect(_strip.strip('bb   axyz   ')).toBe('bb   axyz');
    expect(_strip.strip('   bbaxyz')).toBe('bbaxyz');
    expect(_strip.strip('   bb   axyz')).toBe('bb   axyz');
    expect(_strip.strip('   bb   axyz   ')).toBe('bb   axyz');
});
