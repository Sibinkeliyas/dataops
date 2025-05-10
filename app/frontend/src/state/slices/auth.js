import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    isAuthenticated: false,
    user: null
};

const tasksSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        loginSuccess: (state, action) => {
            state.isAuthenticated = true;
            state.user = action.payload
        },
        logoutSuccess: (state, action) => {
            state.isAuthenticated = false;
            state.user = null
        },
    },
});

export const { loginSuccess, logoutSuccess } = tasksSlice.actions;

export default tasksSlice.reducer;