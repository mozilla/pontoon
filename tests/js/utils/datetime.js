
import Datetime from 'utils/datetime';


test('Datetime constructor', () => {
    let dt = new Datetime(0);

    // this.datetime is set with a new Date
    expect(dt.datetime).toEqual(new Date(0));

    // default locale is en-GB
    expect(dt.locale).toBe('en-GB');

    // locale can be overridden
    dt = new Datetime(1, 'B');
    expect(dt.datetime).toEqual(new Date(1));
    expect(dt.locale).toBe('B');
})


test('Datetime date', () => {
    let dt = new Datetime(7723);
    expect(dt.date).toBe("January 1, 1970");
    expect(dt.time).toBe("12:00:07 AM");
})
