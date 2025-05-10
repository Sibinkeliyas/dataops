import React, { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { toast } from "sonner";
import { createUser, deleteUser, getRoles, getUsers } from "@/utils/api/admin";
import { useSelector } from "react-redux";

const AdminPage = () => {
  const [users, setUsers] = useState([]);
  const [newUser, setNewUser] = useState({ email: "", name: "", role_id: "" });
  const [roles, setRoles] = useState([]);

  const { isAuthenticated, user: loggedUser } = useSelector((state) => state.authReducer);

  const handleAddUser = async () => {
    const validate = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  if(validate.test(newUser.email)) {
    const data = await createUser(newUser);
    if (data.success) {
      await handleGetUsers();
      setNewUser({ email: "", name: "", role_id: roles[0].id });
      toast.success("User added successfully");
    } else {
      toast.error("Failed to add user");
    }
  } else toast.error("Not a valid email")
    
  };

  const handleRemoveUser = async (userId) => {
    const res = await deleteUser(userId);
    if (res.success) {
      await handleGetUsers();
      toast.success("User removed successfully");
    } else {
      toast.error("Failed to remove user");
    }
  };

  const handleGetUsers = async () => {
    const users = await getUsers();
    setUsers(users.data);
  };

  useEffect(() => {
    // Fetch users from the auth.js file
    const fetchUsers = async () => {
      const roles = await getRoles();
      setRoles(roles.data);
      setNewUser({ email: "", name: "", role_id: roles.data[0].id });
      await handleGetUsers();
    };
    fetchUsers();
  }, []);

  return (
    <div className="container mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle>Admin Panel</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-2">Add New User</h2>
            <div className="flex space-x-2">
              <Input
                type="text"
                placeholder="User Name"
                value={newUser.name}
                onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
              />
              <Input
                placeholder="Email"
                type="email"
                value={newUser.email}
                onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
              />
              <select
                className="border rounded px-2 py-1"
                value={newUser.role_id}
                onChange={(e) => setNewUser({ ...newUser, role_id: e.target.value })}
              >
                {roles.map((role, index) => {
                  return (
                    <option key={index} value={role.id}>
                      {role.role}
                    </option>
                  );
                })}
              </select>
              <Button onClick={handleAddUser} disabled={!newUser.email || !newUser.name || !newUser.role_id}>
                Add User
              </Button>
            </div>
          </div>
          <div>
            <h2 className="text-lg font-semibold mb-2">Existing Users</h2>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.email}>
                    <TableCell>{user.name}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>{user.role.role}</TableCell>
                    <TableCell>
                      <Button
                        variant="destructive"
                        disabled={user.email === loggedUser.username}
                        onClick={() => handleRemoveUser(user.id)}
                      >
                        Remove
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminPage;
