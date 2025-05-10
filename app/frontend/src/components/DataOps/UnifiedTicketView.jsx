import React from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { useQuery } from '@tanstack/react-query';
import { fetchUnifiedTickets } from '../../utils/dataFetching';
import { AlertTriangle, CheckCircle, Clock } from 'lucide-react';

const UnifiedTicketView = () => {
  const { data: unifiedTickets, isLoading, error } = useQuery({
    queryKey: ['unifiedTickets'],
    queryFn: fetchUnifiedTickets,
  });

  if (isLoading) return <div>Loading unified ticket data...</div>;
  if (error) return <div>Error loading unified ticket data: {error.message}</div>;

  const getStatusIcon = (status) => {
    switch (status.toLowerCase()) {
      case 'open':
        return <AlertTriangle className="text-yellow-500" />;
      case 'in progress':
        return <Clock className="text-blue-500" />;
      case 'closed':
        return <CheckCircle className="text-green-500" />;
      default:
        return null;
    }
  };

  const getSourceIcon = (source) => {
    switch (source.toLowerCase()) {
      case 'jira':
        return '🔵';
      case 'servicenow':
        return '🟢';
      case 'azure devops':
        return '🔷';
      default:
        return '⚪';
    }
  };

  const ticketsBySource = unifiedTickets.reduce((acc, ticket) => {
    acc[ticket.source] = (acc[ticket.source] || 0) + 1;
    return acc;
  }, {});

  const pieChartData = Object.entries(ticketsBySource).map(([name, value]) => ({ name, value }));
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Unified Ticket View</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <Card>
          <CardHeader>
            <CardTitle>Tickets by Source</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieChartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Ticket Source Legend</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex items-center">
                <span className="mr-2">🔵</span> JIRA
              </div>
              <div className="flex items-center">
                <span className="mr-2">🟢</span> ServiceNow
              </div>
              <div className="flex items-center">
                <span className="mr-2">🔷</span> Azure DevOps
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Ticket ID</TableHead>
            <TableHead>Title</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Priority</TableHead>
            <TableHead>Assigned To</TableHead>
            <TableHead>Source</TableHead>
            <TableHead>Created Date</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {unifiedTickets.map((ticket) => (
            <TableRow key={ticket.id}>
              <TableCell>{ticket.id}</TableCell>
              <TableCell>{ticket.title}</TableCell>
              <TableCell className="flex items-center">
                {getStatusIcon(ticket.status)}
                <span className="ml-2">{ticket.status}</span>
              </TableCell>
              <TableCell>{ticket.priority}</TableCell>
              <TableCell>{ticket.assignedTo}</TableCell>
              <TableCell className="flex items-center">
                {getSourceIcon(ticket.source)}
                <span className="ml-2">{ticket.source}</span>
              </TableCell>
              <TableCell>{ticket.createdDate}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

export default UnifiedTicketView;