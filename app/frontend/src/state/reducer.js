import { combineReducers } from '@reduxjs/toolkit'
import authReducer from './slices/auth'

const reducers = combineReducers({
    authReducer
})

export default reducers