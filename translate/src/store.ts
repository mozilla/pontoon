import { configureStore, ThunkAction, Action } from '@reduxjs/toolkit';

import { reducer } from './rootReducer';

export const store = configureStore({
  // @ts-expect-error Here be dragons
  reducer,

  // @ts-expect-error Here be dragons
  middleware(getDefaultMiddleware) {
    return getDefaultMiddleware({
      serializableCheck: false,
      immutableCheck: false,
    });
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
