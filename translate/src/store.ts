import { configureStore, ThunkAction, Action } from '@reduxjs/toolkit';
import { createLogger } from 'redux-logger';

import { reducer } from './rootReducer';

export const store = configureStore({
  // @ts-expect-error Here be dragons
  reducer,

  // @ts-expect-error Here be dragons
  middleware(getDefaultMiddleware) {
    const middleware = getDefaultMiddleware({
      serializableCheck: false,
      immutableCheck: false,
    });

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
