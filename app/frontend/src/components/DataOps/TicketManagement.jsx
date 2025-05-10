import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { MessageSquare } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { fetchTickets } from '../../utils/dataFetching';
import TeamTickets from './TeamTickets';
import CreateTicket from './CreateTicket';
import UnifiedTicketView from './UnifiedTicketView';
import TicketTable from './TicketTable';
import TicketCharts from './TicketCharts';
import TicketDetails from './TicketDetails';
import TicketDocumentation from './TicketDocumentation';

const TicketManagement = () => {
  const { data: tickets, isLoading, error } = useQuery({
    queryKey: ['tickets'],
    queryFn: fetchTickets,
  });

  const [selectedTicket, setSelectedTicket] = useState(null);

  if (isLoading) return <div>Loading ticket data...</div>;
  if (error) return <div>Error loading ticket data: {error.message}</div>;

  return (
    <div className="space-y-8">
      <Tabs defaultValue="myTickets" className="space-y-4">
        <TabsList className="flex flex-wrap">
          <TabsTrigger value="myTickets">My Tickets</TabsTrigger>
          <TabsTrigger value="teamTickets">Team Tickets</TabsTrigger>
          <TabsTrigger value="createTicket">Create Ticket</TabsTrigger>
          <TabsTrigger value="unifiedView">Unified View</TabsTrigger>
        </TabsList>
        <TabsContent value="myTickets">
          <TicketTable tickets={tickets} onViewDetails={setSelectedTicket} />
          <TicketCharts tickets={tickets} />
        </TabsContent>
        <TabsContent value="teamTickets">
          <TeamTickets />
        </TabsContent>
        <TabsContent value="createTicket">
          <CreateTicket />
        </TabsContent>
        <TabsContent value="unifiedView">
          <UnifiedTicketView />
        </TabsContent>
      </Tabs>

      {selectedTicket && <TicketDetails ticket={selectedTicket} />}

      <TicketDocumentation />
    </div>
  );
};

export default TicketManagement;