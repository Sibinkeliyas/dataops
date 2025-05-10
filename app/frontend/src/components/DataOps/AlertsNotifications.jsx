import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AlertTriangle, Bell, CheckCircle, Info } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { fetchAlerts } from '../../utils/dataFetching';

const AlertsNotifications = () => {
  const { data: alerts, isLoading, error } = useQuery({
    queryKey: ['alerts'],
    queryFn: fetchAlerts,
  });

  const getSeverityIcon = (severity) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return <AlertTriangle className="text-red-500" />;
      case 'medium':
        return <Bell className="text-yellow-500" />;
      case 'low':
        return <Info className="text-blue-500" />;
      default:
        return <CheckCircle className="text-green-500" />;
    }
  };

  if (isLoading) return <div>Loading alerts...</div>;
  if (error) return <div>Error loading alerts: {error.message}</div>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Alerts and Notifications</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {alerts.map((alert) => (
          <Card key={alert.id}>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>{alert.type}</span>
                <span className="flex items-center">
                  {getSeverityIcon(alert.severity)}
                  <span className="ml-2">{alert.severity}</span>
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="mb-2"><strong>Timestamp:</strong> {alert.timestamp}</p>
              <p className="mb-2"><strong>Message:</strong> {alert.message}</p>
              <p className="mb-4"><strong>Affected System:</strong> {alert.affectedSystem}</p>
              <div className="flex justify-end space-x-2">
                <Button variant="outline" size="sm">Acknowledge</Button>
                <Button variant="outline" size="sm">View Details</Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default AlertsNotifications;