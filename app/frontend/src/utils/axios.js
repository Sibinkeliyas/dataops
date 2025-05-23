import axios from "axios";

const axiosInstance = axios.create();

axiosInstance.interceptors.request.use(
    (config) => {
      const accessToken = localStorage.getItem("accessToken")
      if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
      }
      return config;
    },
    (error) => Promise.reject(error),
  );

  export default axiosInstance