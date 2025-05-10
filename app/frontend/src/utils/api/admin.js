import { API_BASE_URL } from "@/config";
import axios from "axios";
import apiConstants from "@/constants/apiConstants";

export const getRoles = async () => {
  try {
    const res = await axios.post(`${API_BASE_URL}/${apiConstants.ADMIN_GET_ROLES}`);
    return res.data;
  } catch (error) {
    throw error;
  }
};

export const getUsers = async () => {
  try {
    const res = await axios.get(`${API_BASE_URL}/${apiConstants.ADMIN_GET_USERS}`);
    return res.data;
  } catch (error) {
    throw error;
  }
};

export const createUser = async (payload) => {
    try {
      const res = await axios.post(`${API_BASE_URL}/${apiConstants.ADMIN_ADD_USER}`, payload);
      return res.data;
    } catch (error) {
      throw error;
    }
  };

  export const deleteUser = async (id) => {
    try {
      const res = await axios.delete(`${API_BASE_URL}/${apiConstants.ADMIN_DELETE_USER}?id=${id}`,);
      return res.data;
    } catch (error) {
        console.log(error);
        
      throw error;
    }
  };
