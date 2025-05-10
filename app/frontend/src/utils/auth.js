let users = [
  { email: 'arda.basar@allnex.com', password: 'lalalalalom69', role: 'admin' },
  { email: 'dennis.vanbregt@allnex.com', password: 'amazingstuff31', role: 'member' },
  { email: 'test@allnex.com', password: 'test678', role: 'member' },
];

export const authenticateUser = (email, password) => {
  const user = users.find(u => u.email === email && u.password === password);
  return user ? true : false;
};

export const logoutUser = (setIsAuthenticated) => {
  setIsAuthenticated(false);
};

export const getUsers = () => {
  return users.map(({ email, role }) => ({ email, role }));
};

export const addUser = (newUser) => {
  if (users.some(user => user.email === newUser.email)) {
    return false;
  }
  users.push(newUser);
  return true;
};

export const removeUser = (email) => {
  const initialLength = users.length;
  users = users.filter(user => user.email !== email);
  return users.length < initialLength;
};