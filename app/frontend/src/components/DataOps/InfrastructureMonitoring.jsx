import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { CheckCircle, AlertTriangle, XCircle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { useQuery } from '@tanstack/react-query';
import { fetchInfrastructureData, fetchUsageData, fetchAzureCostData } from '../../utils/dataFetching';
import ServiceDetailsModal from './ServiceDetailsModal';

const InfrastructureMonitoring = () => {
  const { data: infrastructureData, isLoading: infraLoading } = useQuery({
    queryKey: ['infrastructureData'],
    queryFn: fetchInfrastructureData,
  });

  const { data: usageData, isLoading: usageLoading } = useQuery({
    queryKey: ['usageData'],
    queryFn: fetchUsageData,
  });

  const { data: azureCostData, isLoading: costLoading } = useQuery({
    queryKey: ['azureCostData'],
    queryFn: fetchAzureCostData,
  });

  const getStatusIcon = (status) => {
    switch (status.toLowerCase()) {
      case 'operational':
        return <CheckCircle className="text-green-500" />;
      case 'warning':
        return <AlertTriangle className="text-yellow-500" />;
      case 'issue':
        return <XCircle className="text-red-500" />;
      default:
        return null;
    }
  };

  if (infraLoading || usageLoading || costLoading) {
    return <div>Loading infrastructure data...</div>;
  }

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82ca9d', '#ffc658', '#8dd1e1', '#a4de6c', '#d0ed57'];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Azure and Databricks Platform Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[150px]">Service</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="hidden sm:table-cell">Metric 1</TableHead>
                  <TableHead className="hidden md:table-cell">Metric 2</TableHead>
                  <TableHead className="hidden lg:table-cell">Metric 3</TableHead>
                  <TableHead className="sm:hidden">Details</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {infrastructureData.services.map((service) => (
                  <TableRow key={service.name}>
                    <TableCell className="font-medium">{service.name}</TableCell>
                    <TableCell className="flex items-center">
                      {getStatusIcon(service.status)}
                      <span className="ml-2">{service.status}</span>
                    </TableCell>
                    {Object.entries(service).slice(2, 5).map(([key, value], index) => (
                      <TableCell key={index} className={`hidden ${index === 0 ? 'sm:table-cell' : index === 1 ? 'md:table-cell' : 'lg:table-cell'}`}>
                        {`${key}: ${value}`}
                      </TableCell>
                    ))}
                    <TableCell className="sm:hidden">
                      <ServiceDetailsModal service={service} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Resource Utilization Over Time</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={infrastructureData.utilizationHistory}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="cpuUsage" stroke="#8884d8" name="CPU Usage" />
              <Line type="monotone" dataKey="memoryUsage" stroke="#82ca9d" name="Memory Usage" />
              <Line type="monotone" dataKey="storageUsage" stroke="#ffc658" name="Storage Usage" />
              <Line type="monotone" dataKey="networkUsage" stroke="#ff7300" name="Network Usage" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Fabric and Power BI Usage Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={usageData.metrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="activeUsers" fill="#8884d8" name="Active Users" />
              <Bar dataKey="reportsViewed" fill="#82ca9d" name="Reports Viewed" />
              <Bar dataKey="queriesRun" fill="#ffc658" name="Queries Run" />
              <Bar dataKey="dataProcessed" fill="#ff7300" name="Data Processed (GB)" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Top Power BI Reports</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Report Name</TableHead>
                <TableHead>Views</TableHead>
                <TableHead>Unique Users</TableHead>
                <TableHead>Avg. Load Time</TableHead>
                <TableHead>Data Size</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {usageData.topReports.map((report) => (
                <TableRow key={report.name}>
                  <TableCell>{report.name}</TableCell>
                  <TableCell>{report.views}</TableCell>
                  <TableCell>{report.uniqueUsers}</TableCell>
                  <TableCell>{report.avgLoadTime}s</TableCell>
                  <TableCell>{report.dataSize}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Azure Cost Dashboard</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold mb-2">Monthly Cost Trend</h3>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={azureCostData.monthlyCosts}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="cost" stroke="#8884d8" />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-2">Service Cost Breakdown</h3>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={azureCostData.serviceBreakdown}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="cost"
                  >
                    {azureCostData.serviceBreakdown.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="mt-4">
            <h3 className="text-lg font-semibold mb-2">Cost Summary</h3>
            <p>Total Cost: ${azureCostData.totalCost}</p>
            <p>Budget Limit: ${azureCostData.budgetLimit}</p>
            <p>Remaining Budget: ${azureCostData.budgetLimit - azureCostData.totalCost}</p>
            <p>Cost Trend: {azureCostData.costTrend}</p>
          </div>
          <div className="mt-4">
            <h3 className="text-lg font-semibold mb-2">Savings Opportunities</h3>
            <ul>
              {azureCostData.savingsOpportunities.map((opportunity, index) => (
                <li key={index}>{opportunity.description}: ${opportunity.potentialSavings} potential savings</li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default InfrastructureMonitoring;
