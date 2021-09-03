import { configureStore, ThunkAction, Action } from '@reduxjs/toolkit';
import { createLogger } from 'redux-logger';
import { routerMiddleware } from 'connected-react-router';

import history from './historyInstance';
import createRootReducer from './rootReducer';

const store = configureStore({
    reducer: createRootReducer(history),
    middleware: (getDefaultMiddleware) => {
        const middleware = getDefaultMiddleware({
            serializableCheck: false,
            immutableCheck: false,
        }).prepend(routerMiddleware(history));
        if (process.env.NODE_ENV === 'development') {
            middleware.push(createLogger());
        }
        return middleware;
    },
});

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
export type AppThunk<ReturnType = void> = ThunkAction<
    ReturnType,
    RootState,
    unknown,
    Action<string>
>;

export default store;
