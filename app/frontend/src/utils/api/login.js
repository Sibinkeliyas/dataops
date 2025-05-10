import { API_BASE_URL } from "@/config";
import axios from "axios";
import apiConstants from "@/constants/apiConstants";

export const loginUser = async (payload) => {
  try {
    const res = await axios.post(`${API_BASE_URL}/${apiConstants.USER_LOGIN}`, {
      ...payload,
      role_id: "8c6684e0-faf5-45b4-9fb1-5daf505f676f",
    });
    return res.data;
  } catch (error) {
    throw error;
  }
};

export const getUser = async (email) => {
    try {
      const res = await axios.get(`${API_BASE_URL}/${apiConstants.GET_USER}?email=${email}`);
      return res.data;
    } catch (error) {
      throw error;
    }
  };
  
