import { configureStore } from '@reduxjs/toolkit';

// Placeholder store - will add slices later
export const store = configureStore({
  reducer: {
    // Add reducers here as we build them
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
