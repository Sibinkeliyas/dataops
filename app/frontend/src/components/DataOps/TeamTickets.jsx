import React from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useQuery } from '@tanstack/react-query';
import { fetchTeamTickets } from '../../utils/dataFetching';

const TeamTickets = () => {
  const { data: teamTickets, isLoading, error } = useQuery({
    queryKey: ['teamTickets'],
    queryFn: fetchTeamTickets,
  });

  if (isLoading) return <div>Loading team ticket data...</div>;
  if (error) return <div>Error loading team ticket data: {error.message}</div>;

  const ticketsByMember = teamTickets.reduce((acc, ticket) => {
    acc[ticket.assignedTo] = (acc[ticket.assignedTo] || 0) + 1;
    return acc;
  }, {});

  const ticketDistributionData = Object.entries(ticketsByMember).map(([name, count]) => ({ name, count }));

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Team Tickets</h2>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Ticket ID</TableHead>
            <TableHead>Title</TableHead>
            <TableHead>Assigned To</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Priority</TableHead>
            <TableHead>Created Date</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {teamTickets.map((ticket) => (
            <TableRow key={ticket.id}>
              <TableCell>{ticket.id}</TableCell>
              <TableCell>{ticket.title}</TableCell>
              <TableCell>{ticket.assignedTo}</TableCell>
              <TableCell>{ticket.status}</TableCell>
              <TableCell>{ticket.priority}</TableCell>
              <TableCell>{ticket.createdDate}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Ticket Distribution by Team Member</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={ticketDistributionData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
};

export default TeamTickets;