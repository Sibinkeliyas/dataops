import React from 'react';
import { Link } from 'react-router-dom';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import Dashboard from '../components/DataOps/Dashboard';
import PerformanceGraphs from '../components/DataOps/PerformanceGraphs';
import InfrastructureMonitoring from '../components/DataOps/InfrastructureMonitoring';
import PipelineMonitoring from '../components/DataOps/PipelineMonitoring';
import AlertsNotifications from '../components/DataOps/AlertsNotifications';
import TicketManagement from '../components/DataOps/TicketManagement';

const DataOpsPortal = () => {
  return (
    <div className="container mx-auto px-2 sm:px-4 py-4 sm:py-8">
      <nav className="text-sm mb-4" aria-label="Breadcrumb">
        <ol className="list-none p-0 inline-flex">
          <li className="flex items-center">
            <Link to="/" className="text-blue-500">Home</Link>
            <span className="mx-2">/</span>
          </li>
          <li className="flex items-center">
            DataOps Portal
          </li>
        </ol>
      </nav>

      <h1 className="text-2xl sm:text-3xl font-bold mb-4 sm:mb-6">DataOps Portal</h1>

      <Tabs defaultValue="dashboard" className="space-y-4">
        <TabsList className="flex flex-wrap justify-start gap-2 mb-4">
          <TabsTrigger value="dashboard" className="text-xs sm:text-sm">Dashboard</TabsTrigger>
          <TabsTrigger value="infrastructure" className="text-xs sm:text-sm">Infrastructure</TabsTrigger>
          <TabsTrigger value="pipelines" className="text-xs sm:text-sm">Pipelines</TabsTrigger>
          <TabsTrigger value="performance" className="text-xs sm:text-sm">Performance</TabsTrigger>
          <TabsTrigger value="alerts" className="text-xs sm:text-sm">Alerts</TabsTrigger>
          <TabsTrigger value="tickets" className="text-xs sm:text-sm">Tickets</TabsTrigger>
        </TabsList>
        <div className="mt-4">
          <TabsContent value="dashboard">
            <Dashboard />
          </TabsContent>
          <TabsContent value="infrastructure">
            <InfrastructureMonitoring />
          </TabsContent>
          <TabsContent value="pipelines">
            <PipelineMonitoring />
          </TabsContent>
          <TabsContent value="performance">
            <PerformanceGraphs />
          </TabsContent>
          <TabsContent value="alerts">
            <AlertsNotifications />
          </TabsContent>
          <TabsContent value="tickets">
            <TicketManagement />
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
};

export default DataOpsPortal;