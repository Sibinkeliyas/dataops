import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const DashboardList = ({ dashboards, isLoading, error, onSelectDashboard }) => {
  if (isLoading) return <div>Loading dashboards...</div>;
  if (error) return <div>Error loading dashboards: {error.message}</div>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {dashboards.map((dashboard) => (
        <Card key={dashboard.id}>
          <CardHeader>
            <CardTitle>{dashboard.name}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm mb-4">{dashboard.description}</p>
            <Button onClick={() => onSelectDashboard(dashboard)}>View Details</Button>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default DashboardList;