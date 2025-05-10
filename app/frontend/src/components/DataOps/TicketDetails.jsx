import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { MessageSquare } from 'lucide-react';

const TicketDetails = ({ ticket }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Ticket Details</CardTitle>
      </CardHeader>
      <CardContent>
        <h3 className="text-xl font-semibold mb-4">{ticket.title}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <p><strong>Status:</strong> {ticket.status}</p>
          <p><strong>Priority:</strong> {ticket.priority}</p>
          <p><strong>Assigned To:</strong> {ticket.assignedTo}</p>
          <p><strong>Created Date:</strong> {ticket.createdDate}</p>
          <p><strong>Last Updated:</strong> {ticket.lastUpdated}</p>
          <p><strong>Source:</strong> {ticket.source}</p>
        </div>
        <div className="mt-4">
          <h4 className="font-semibold">Description</h4>
          <p>{ticket.description}</p>
        </div>
        <div className="mt-4">
          <h4 className="font-semibold">Activity Log</h4>
          <ul className="list-disc list-inside">
            {ticket.activityLog.map((activity, index) => (
              <li key={index}>{activity}</li>
            ))}
          </ul>
        </div>
        <div className="mt-4 flex space-x-2">
          <Button variant="outline" className="flex items-center">
            <MessageSquare className="mr-2" />
            Add Comment
          </Button>
          <Button variant="outline">Update Status</Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default TicketDetails;