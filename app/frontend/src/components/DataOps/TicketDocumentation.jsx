import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const TicketDocumentation = () => {
  return (
    <Card className="mt-8">
      <CardHeader>
        <CardTitle>Documentation</CardTitle>
      </CardHeader>
      <CardContent>
        <h3 className="text-lg font-semibold mb-2">Ticket Management Guidelines</h3>
        <ul className="list-disc list-inside">
          <li>Always provide a clear and concise title for new tickets</li>
          <li>Assign appropriate priority based on impact and urgency</li>
          <li>Update ticket status promptly as progress is made</li>
          <li>Include all relevant information in the ticket description</li>
          <li>Use comments to communicate updates and ask questions</li>
        </ul>
        <h3 className="text-lg font-semibold mt-4 mb-2">Ticket Lifecycle</h3>
        <ol className="list-decimal list-inside">
          <li>Open: Ticket is created and awaiting assignment</li>
          <li>In Progress: Work has begun on resolving the ticket</li>
          <li>Pending: Awaiting input from the requester or third party</li>
          <li>Resolved: The issue has been addressed</li>
          <li>Closed: The ticket is completed and verified</li>
        </ol>
      </CardContent>
    </Card>
  );
};

export default TicketDocumentation;