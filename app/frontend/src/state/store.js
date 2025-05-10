import { configureStore } from '@reduxjs/toolkit';
import tasksReducer from './slices/auth';
import reducers from './reducer';


const store = configureStore({
    reducer: reducers,
    middleware: (getDefaultMiddleware) => getDefaultMiddleware(),
});
export default store;