import React from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { AlertTriangle, CheckCircle, Clock, FileText } from 'lucide-react';

const TicketTable = ({ tickets, onViewDetails }) => {
  const getStatusIcon = (status) => {
    switch (status.toLowerCase()) {
      case 'open': return <AlertTriangle className="text-yellow-500" />;
      case 'in progress': return <Clock className="text-blue-500" />;
      case 'closed': return <CheckCircle className="text-green-500" />;
      default: return <FileText className="text-gray-500" />;
    }
  };

  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[100px]">ID</TableHead>
            <TableHead>Title</TableHead>
            <TableHead className="hidden md:table-cell">Status</TableHead>
            <TableHead className="hidden md:table-cell">Assigned To</TableHead>
            <TableHead className="hidden lg:table-cell">Created Date</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {tickets.map((ticket) => (
            <TableRow key={ticket.id}>
              <TableCell className="font-medium">{ticket.id}</TableCell>
              <TableCell>{ticket.title}</TableCell>
              <TableCell className="hidden md:table-cell">
                <span className="flex items-center">
                  {getStatusIcon(ticket.status)}
                  <span className="ml-2">{ticket.status}</span>
                </span>
              </TableCell>
              <TableCell className="hidden md:table-cell">{ticket.assignedTo}</TableCell>
              <TableCell className="hidden lg:table-cell">{ticket.createdDate}</TableCell>
              <TableCell>
                <Button variant="outline" size="sm" onClick={() => onViewDetails(ticket)}>View</Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

export default TicketTable;