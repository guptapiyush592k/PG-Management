import { useEffect } from 'react';
import { RouterProvider } from 'react-router-dom';
import { AppProviders } from './providers';
import { router } from './router';
import { store } from './store';

function ThemeInit() {
  useEffect(() => {
    const theme = store.getState().ui.theme;
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, []);
  return null;
}

export function App() {
  return (
    <AppProviders>
      <ThemeInit />
      <RouterProvider router={router} />
    </AppProviders>
  );
}
