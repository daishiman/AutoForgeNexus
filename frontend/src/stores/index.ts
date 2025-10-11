import { create } from 'zustand';
import { devtools, persist, subscribeWithSelector } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

// User型定義
interface User {
  id: string;
  email: string;
  name: string;
  createdAt: Date;
  updatedAt: Date;
}

// Notification型定義
interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  createdAt: Date;
}

// ユーザーストアの型定義
interface UserState {
  user: User | null;
  isLoading: boolean;
  error: string | null;
}

interface UserActions {
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

type UserStore = UserState & UserActions;

// ユーザーストア
export const useUserStore = create<UserStore>()(
  devtools(
    persist(
      immer((set) => ({
        // 状態
        user: null,
        isLoading: false,
        error: null,

        // アクション
        setUser: (user) =>
          set((state) => {
            state.user = user;
          }),

        setLoading: (loading) =>
          set((state) => {
            state.isLoading = loading;
          }),

        setError: (error) =>
          set((state) => {
            state.error = error;
          }),

        reset: () =>
          set((state) => {
            state.user = null;
            state.isLoading = false;
            state.error = null;
          }),
      })),
      {
        name: 'user-storage',
        partialize: (state) => ({ user: state.user }),
      },
    ),
    {
      name: 'user-store',
    },
  ),
);

// アプリケーションストアの型定義
interface AppState {
  theme: 'light' | 'dark' | 'system';
  sidebarOpen: boolean;
  notifications: Notification[];
}

interface AppActions {
  setTheme: (theme: AppState['theme']) => void;
  toggleSidebar: () => void;
  addNotification: (notification: Notification) => void;
  removeNotification: (id: string) => void;
}

type AppStore = AppState & AppActions;

// アプリケーションストア
export const useAppStore = create<AppStore>()(
  devtools(
    persist(
      subscribeWithSelector(
        immer((set) => ({
          // 状態
          theme: 'system',
          sidebarOpen: true,
          notifications: [],

          // アクション
          setTheme: (theme) =>
            set((state) => {
              state.theme = theme;
            }),

          toggleSidebar: () =>
            set((state) => {
              state.sidebarOpen = !state.sidebarOpen;
            }),

          addNotification: (notification) =>
            set((state) => {
              state.notifications.push(notification);
            }),

          removeNotification: (id) =>
            set((state) => {
              state.notifications = state.notifications.filter((n: Notification) => n.id !== id);
            }),
        })),
      ),
      {
        name: 'app-storage',
        partialize: (state) => ({ theme: state.theme }),
      },
    ),
    {
      name: 'app-store',
    },
  ),
);
