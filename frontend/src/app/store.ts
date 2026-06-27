import { configureStore, createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { ThemeMode } from '@/shared/types/api.types';

interface UiState {
  sidebarCollapsed: boolean;
  mobileSidebarOpen: boolean;
  theme: ThemeMode;
}

const initialState: UiState = {
  sidebarCollapsed: false,
  mobileSidebarOpen: false,
  theme: (localStorage.getItem('pg-theme') as ThemeMode) || 'light',
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarCollapsed = !state.sidebarCollapsed;
    },
    setSidebarCollapsed: (state, action: PayloadAction<boolean>) => {
      state.sidebarCollapsed = action.payload;
    },
    toggleMobileSidebar: (state) => {
      state.mobileSidebarOpen = !state.mobileSidebarOpen;
    },
    setMobileSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.mobileSidebarOpen = action.payload;
    },
    setTheme: (state, action: PayloadAction<ThemeMode>) => {
      state.theme = action.payload;
      localStorage.setItem('pg-theme', action.payload);
    },
  },
});

export const {
  toggleSidebar,
  setSidebarCollapsed,
  toggleMobileSidebar,
  setMobileSidebarOpen,
  setTheme,
} = uiSlice.actions;

export const store = configureStore({
  reducer: { ui: uiSlice.reducer },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
