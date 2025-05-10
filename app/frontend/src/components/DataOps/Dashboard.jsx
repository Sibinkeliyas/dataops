import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle, AlertTriangle, XCircle } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { fetchDashboardData } from '../../utils/dataFetching';

const StatusIcon = ({ status }) => {
  switch (status.toLowerCase()) {
    case 'healthy':
      return <CheckCircle className="text-green-500" />;
    case 'warning':
      return <AlertTriangle className="text-yellow-500" />;
    case 'critical':
      return <XCircle className="text-red-500" />;
    default:
      return null;
  }
};

const Dashboard = () => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboardData'],
    queryFn: fetchDashboardData,
  });

  if (isLoading) return <div>Loading dashboard data...</div>;
  if (error) return <div>Error loading dashboard data: {error.message}</div>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <Card>
        <CardHeader>
          <CardTitle>Infrastructure Health</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-2">
            <StatusIcon status={data.infrastructureStatus} />
            <span>{data.infrastructureStatus}</span>
          </div>
          <p>Uptime: {data.uptime}</p>
          <p>Active Alerts: {data.activeInfraAlerts}</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Pipeline Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-2">
            <StatusIcon status={data.pipelineStatus} />
            <span>{data.pipelineStatus}</span>
          </div>
          <p>Success Rate: {data.pipelineSuccessRate}</p>
          <p>Failed Jobs: {data.failedJobs}</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Data Quality</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-2">
            <StatusIcon status={data.dataQualityStatus} />
            <span>{data.dataQualityStatus}</span>
          </div>
          <p>Quality Score: {data.dataQualityScore}</p>
          <p>Issues Detected: {data.dataQualityIssues}</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Cost Management</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-2">
            <StatusIcon status={data.costStatus} />
            <span>{data.costStatus}</span>
          </div>
          <p>Monthly Spend: ${data.monthlySpend}</p>
          <p>Budget Utilization: {data.budgetUtilization}%</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Security & Compliance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-2">
            <StatusIcon status={data.securityStatus} />
            <span>{data.securityStatus}</span>
          </div>
          <p>Open Vulnerabilities: {data.openVulnerabilities}</p>
          <p>Compliance Score: {data.complianceScore}%</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Support Tickets</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-2">
            <StatusIcon status={data.ticketStatus} />
            <span>{data.ticketStatus}</span>
          </div>
          <p>Open Tickets: {data.openTickets}</p>
          <p>Avg. Resolution Time: {data.avgResolutionTime}</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;